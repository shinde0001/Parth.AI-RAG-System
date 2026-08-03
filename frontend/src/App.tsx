import { useState, useRef, useEffect } from 'react';
import type { ChangeEvent } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, FileText, Upload, Trash2, ChevronDown, ChevronUp, Bot, User, Link } from 'lucide-react';
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
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
        body: JSON.stringify({ query: userMessage.content, top_k: 5, temperature: 0.1 })
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
      
      // Optionally reset the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      alert(`Upload Failed: ${error.message || 'Server error'}`);
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
    } catch (error: any) {
      console.error('Link upload error:', error);
      alert(`Link Failed: ${error.message || 'Server error'}`);
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
      }
    } catch (error) {
      console.error('Failed to delete document', error);
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
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="brand-icon">P</div>
          <div className="brand-name">Parth.AI</div>
        </div>

        <div className="sidebar-section">
          <h3>Knowledge Base</h3>
          
          <div className="document-list">
            {documents.map(doc => (
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
            ))}
          </div>
          
          <div style={{ marginTop: '16px' }}>
            <form onSubmit={handleLinkSubmit} style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
              <input 
                type="url" 
                placeholder="Paste web link..." 
                value={linkInput}
                onChange={(e) => setLinkInput(e.target.value)}
                style={{ flexGrow: 1, padding: '8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-medium)' }}
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
            <h1>Good afternoon, Parth</h1>
            <p>I'm an AI assistant grounded in your specific documents. Upload a file to the Knowledge Base, then ask me anything about it.</p>
          </div>
        ) : (
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
        )}

        {/* Input Box */}
        <div className="input-container">
          <div className="input-box">
            <textarea
              value={input}
              onChange={autoResizeTextarea}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything..."
              rows={1}
            />
            <button 
              className="send-btn" 
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              {isLoading ? <span className="loader"></span> : <Send size={16} />}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
