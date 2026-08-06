import { useState, useRef, useEffect } from 'react';
import type { ChangeEvent } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, FileText, Upload, Trash2, ChevronDown, ChevronUp, Bot, User, Link, Mic, MicOff, AudioLines, Plus, Moon, Sun } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import './index.css';

interface Source {
  filename: string;
  chunk_text: string;
  similarity_score: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface Document {
  id: string;
  filename: string;
}

const API_URL = 'http://localhost:8000/api/v1';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [expandedSources, setExpandedSources] = useState<string[]>([]);
  const [linkInput, setLinkInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  }, [isDarkMode]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  const speakText = (text: string) => {
    if (!('speechSynthesis' in window)) return;
    
    // Stop any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    
    // By not forcing a specific English voice, the browser will automatically 
    // attempt to use the correct voice/language pack for the text content.
    window.speechSynthesis.speak(utterance);
  };

  const toggleListening = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in your browser.');
      return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      // Removed hardcoded 'en-US' to allow the browser to auto-detect or use system default language

      recognition.onresult = (event: any) => {
        let currentTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setInput(currentTranscript);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
      recognitionRef.current = recognition;
      setIsListening(true);
    } catch (err) {
      console.error(err);
      setIsListening(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: userMessage.content, 
          top_k: 5, 
          temperature: 0.1,
          document_ids: documents.length > 0 ? documents.map(d => d.id) : undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to fetch response');
      }

      const data = await response.json();
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      if (isVoiceMode) {
        speakText(data.answer);
      }
    } catch (error: any) {
      console.error(error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error.message || 'Sorry, I encountered an error communicating with the server.'}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const autoResizeTextarea = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = e.target.scrollHeight + 'px';
  };

  const handleFileUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/documents/upload`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Upload failed');
      }
      
      const data = await response.json();
      setDocuments(prev => [...prev, { id: data.document_id, filename: file.name }]);
      toast.success('Document uploaded successfully');
      
      // Optionally reset the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(`Upload Failed: ${error.message || 'Server error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleLinkSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!linkInput.trim()) return;

    setIsUploading(true);
    try {
      const response = await fetch(`${API_URL}/documents/link`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: linkInput.trim() })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Link processing failed');
      }
      
      const data = await response.json();
      setDocuments(prev => [...prev, { id: data.document_id, filename: linkInput }]);
      setLinkInput('');
      toast.success('Link ingested successfully');
    } catch (error: any) {
      console.error('Link upload error:', error);
      toast.error(`Link Failed: ${error.message || 'Server error'}`);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (id: string) => {
    try {
      const response = await fetch(`${API_URL}/documents/${id}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        setDocuments(prev => prev.filter(doc => doc.id !== id));
        toast.success('Document deleted');
      }
    } catch (error) {
      console.error('Failed to delete document', error);
      toast.error('Failed to delete document');
    }
  };

  const toggleSources = (messageId: string) => {
    setExpandedSources(prev => 
      prev.includes(messageId) 
        ? prev.filter(id => id !== messageId)
        : [...prev, messageId]
    );
  };

  return (
    <div className="app-container">
      <Toaster position="top-right" toastOptions={{
        style: {
          background: 'var(--bg-main)',
          color: 'var(--text-primary)',
          border: '1px solid var(--border-medium)',
        },
      }} />
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header" style={{ display: 'flex', flexDirection: 'column', gap: '16px', alignItems: 'stretch' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div className="brand-icon">P</div>
              <div className="brand-name">Parth.AI</div>
            </div>
            <button 
              onClick={() => setIsDarkMode(!isDarkMode)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}
              title="Toggle Dark Mode"
            >
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </button>
          </div>
          <button 
            onClick={() => setMessages([])}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '10px', background: 'var(--bg-input)', border: '1px solid var(--border-medium)', borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)', cursor: 'pointer', fontWeight: 500, transition: 'all 0.2s' }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = 'var(--border-medium)'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-input)'}
          >
            <Plus size={16} /> New Chat
          </button>
        </div>

        <div className="sidebar-section">
          <h3>Knowledge Base</h3>
          
          <div className="document-list">
            {documents.length === 0 ? (
              <div className="empty-docs-notice">
                <span>No documents added yet</span>
              </div>
            ) : (
              documents.map(doc => (
                <div key={doc.id} className="document-item">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileText size={14} color="var(--text-secondary)" />
                    <span className="doc-name" title={doc.filename}>{doc.filename}</span>
                  </div>
                  <button 
                    className="delete-btn" 
                    onClick={() => handleDeleteDocument(doc.id)}
                    title="Delete Document"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
          
          <div style={{ marginTop: '16px' }}>
            <form onSubmit={handleLinkSubmit} style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
              <input 
                type="url" 
                placeholder="Paste web link..." 
                value={linkInput}
                onChange={(e) => setLinkInput(e.target.value)}
                style={{ flexGrow: 1, padding: '8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-medium)', background: 'var(--bg-main)', color: 'var(--text-primary)' }}
                required
              />
              <button 
                type="submit"
                disabled={isUploading || !linkInput.trim()}
                style={{ padding: '8px 12px', background: 'var(--brand-color)', color: 'white', border: 'none', borderRadius: 'var(--radius-sm)', cursor: 'pointer' }}
              >
                <Link size={14} />
              </button>
            </form>

            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              onChange={handleFileUpload}
              accept=".txt,.pdf,.md,.docx"
            />
            <button 
              className="upload-btn"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              {isUploading ? <span className="loader" style={{ borderColor: 'var(--text-primary)', borderTopColor: 'transparent' }}></span> : <Upload size={16} />}
              {isUploading ? 'Uploading...' : 'Upload Document'}
            </button>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="chat-area">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-logo">P</div>
            <h2 className="empty-state-title">What would you like to know today?</h2>
            <p className="empty-state-subtitle">I'm an AI assistant grounded in your specific documents. Upload a file to the Knowledge Base or paste a web link to get started.</p>
            
            <div className="input-box empty-state-input">
              <textarea
                value={input}
                onChange={autoResizeTextarea}
                onKeyDown={handleKeyDown}
                placeholder={isListening ? "Listening... Speak now" : "Ask anything about your documents..."}
                rows={1}
              />
              <button 
                type="button"
                className={`mic-btn ${isListening ? 'listening' : ''}`}
                onClick={toggleListening}
                title={isListening ? "Stop listening" : "Voice input (Speech to text)"}
              >
                {isListening ? <MicOff size={16} /> : <Mic size={16} />}
              </button>
              <button 
                type="button"
                className={`voice-mode-btn ${isVoiceMode ? 'active' : ''}`}
                onClick={() => {
                  setIsVoiceMode(!isVoiceMode);
                  if (isVoiceMode) window.speechSynthesis.cancel();
                }}
                title={isVoiceMode ? "Voice Output: ON (Female Voice)" : "Voice Output: OFF"}
              >
                <AudioLines size={16} className={isVoiceMode ? 'wave-animated' : ''} />
              </button>
              <button 
                className="send-btn" 
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
              >
                {isLoading ? <span className="loader"></span> : <Send size={16} />}
              </button>
            </div>

            <div className="suggestion-chips">
              <button 
                className="chip-btn" 
                onClick={() => setInput("Summarize the key points from my uploaded documents.")}
              >
                📄 Summarize key insights
              </button>
              <button 
                className="chip-btn" 
                onClick={() => setInput("What are the main topics covered in this knowledge base?")}
              >
                🔍 Analyze main topics
              </button>
              <button 
                className="chip-btn" 
                onClick={() => setInput("Extract key action items and decisions.")}
              >
                💡 Extract action items
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="chat-history">
              {messages.map((msg) => (
                <div key={msg.id} className={`message-wrapper ${msg.role}`}>
                  <div className={`message ${msg.role}`}>
                    <div className={`avatar ${msg.role}`}>
                      {msg.role === 'assistant' ? <Bot size={20} /> : <User size={20} />}
                    </div>
                    
                    <div className={`message-content ${msg.role === 'assistant' ? 'markdown-body' : ''}`}>
                      {msg.role === 'assistant' ? (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                      ) : (
                        <p>{msg.content}</p>
                      )}
                      
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="sources-accordion">
                          <div 
                            className="sources-header"
                            onClick={() => toggleSources(msg.id)}
                          >
                            <span>{msg.sources.length} sources used</span>
                            {expandedSources.includes(msg.id) ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </div>
                          
                          {expandedSources.includes(msg.id) && (
                            <div className="sources-body">
                              {msg.sources.map((src, idx) => (
                                <div key={idx} className="source-item">
                                  <div className="source-item-header">
                                    {src.filename} <span style={{ color: 'var(--text-tertiary)', fontSize: '11px', fontWeight: 'normal', marginLeft: '8px' }}>Match: {(src.similarity_score * 100).toFixed(1)}%</span>
                                  </div>
                                  <div className="source-item-text">
                                    {src.chunk_text}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Box for active chat */}
            <div className="input-container">
              <div className="input-box">
                <textarea
                  value={input}
                  onChange={autoResizeTextarea}
                  onKeyDown={handleKeyDown}
                  placeholder={isListening ? "Listening... Speak now" : "Ask anything..."}
                  rows={1}
                />
                <button 
                  type="button"
                  className={`mic-btn ${isListening ? 'listening' : ''}`}
                  onClick={toggleListening}
                  title={isListening ? "Stop listening" : "Voice input (Speech to text)"}
                >
                  {isListening ? <MicOff size={16} /> : <Mic size={16} />}
                </button>
                <button 
                  type="button"
                  className={`voice-mode-btn ${isVoiceMode ? 'active' : ''}`}
                  onClick={() => {
                    setIsVoiceMode(!isVoiceMode);
                    if (isVoiceMode) window.speechSynthesis.cancel();
                  }}
                  title={isVoiceMode ? "Voice Output: ON (Female Voice)" : "Voice Output: OFF"}
                >
                  <AudioLines size={16} className={isVoiceMode ? 'wave-animated' : ''} />
                </button>
                <button 
                  className="send-btn" 
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                >
                  {isLoading ? <span className="loader"></span> : <Send size={16} />}
                </button>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
