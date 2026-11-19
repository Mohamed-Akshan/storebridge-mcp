
import { useEffect, useRef, useState } from 'react';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import {
  ArrowUp,
  Bot,
  Database,
  LoaderCircle,
  Plus,
  Sparkles,
} from 'lucide-react';

import SalesChart from './SalesChart.jsx';


const ownerPrompts = [
  'Compare sales across all branches this month',
  'Which salesperson generated the highest revenue?',
  'Check Samsung Galaxy S26 Ultra stock across branches',
  'Which accessories have the highest gross margin?',
];


const managerPrompts = [
  'Check Samsung Galaxy S26 Ultra stock across branches',
  'Compare iPhone selling prices and purchase costs',
  'Which chargers are low in stock at Liberty Plaza?',
  'Do we have accessories for Samsung Galaxy S26 Ultra?',
];


function MarkdownAnswer({ content }) {
  return (
    <div className="markdown-body">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          table: ({ children }) => (
            <div className="chat-table-container">
              <table className="chat-result-table">
                {children}
              </table>
            </div>
          ),

          h2: ({ children }) => (
            <h2 className="chat-answer-heading">
              {children}
            </h2>
          ),

          h3: ({ children }) => (
            <h3 className="chat-answer-subheading">
              {children}
            </h3>
          ),

          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
        }}
      >
        {typeof content === 'string' ? content : ''}
      </ReactMarkdown>
    </div>
  );
}


function AssistantMessage({ message }) {
  return (
    <div className="chat-message assistant">

      <span className="message-avatar">
        <Bot size={17} />
      </span>

      <div className="message-body">

        <div className="message-author">
          <span>Walk & Talk Assistant</span>
        </div>

        <MarkdownAnswer content={message.content} />

        {message.chart && (
          <div className="chat-chart-section">
            <SalesChart chart={message.chart} />
          </div>
        )}

        {message.tools_used?.length > 0 && (
          <div className="source-line">
            <Database size={13} />

            <span>
              Data retrieved using{' '}
              {message.tools_used.join(', ')}
            </span>
          </div>
        )}

      </div>
    </div>
  );
}


function UserMessage({ message }) {
  return (
    <div className="chat-message user">
      <div className="message-body">
        <div className="user-message-text">
          {message.content}
        </div>
      </div>
    </div>
  );
}


export default function ChatWindow({
  user,
  messages,
  setMessages,
  ask,
  busy,
  error,
}) {
  const [draft, setDraft] = useState('');

  const bottom = useRef(null);

  const prompts = (
    user.role === 'manager'
      ? managerPrompts
      : ownerPrompts
  );


  useEffect(() => {
    bottom.current?.scrollIntoView({
      behavior: 'smooth',
    });
  }, [messages, busy]);


  function submit(event) {
    event.preventDefault();

    const question = draft.trim();

    if (!question || busy) {
      return;
    }

    ask(question);

    setDraft('');
  }


  function newChat() {
    if (busy) {
      return;
    }

    setMessages([]);

    setDraft('');
  }


  return (
    <div className="chat-pane">

      <header className="page-header chat-header">

        <div>
          <div className="eyebrow">
            YOUR AI WORKSPACE
          </div>

          <h1>
            Walk & Talk Assistant
          </h1>

          <p>
            Inventory, pricing and business intelligence
            across your branches.
          </p>
        </div>

        <button
          type="button"
          className="outline-button small"
          onClick={newChat}
          disabled={busy}
        >
          <Plus size={16} />
          New chat
        </button>

      </header>


      <div className="chat-scroller">

        {messages.length === 0 && (
          <div className="chat-empty">

            <div className="assistant-emblem">
              <Sparkles size={27} />
            </div>

            <h2>
              Good to see you,{' '}
              {user.name?.split(' ')[0] || 'there'}.
            </h2>

            <p>
              I'm here to help you understand your
              Walk & Talk business data across all
              three branches.
            </p>

            <div className="prompt-grid">
              {prompts.map((prompt) => (
                <button
                  type="button"
                  key={prompt}
                  onClick={() => ask(prompt)}
                  disabled={busy}
                >
                  <span>{prompt}</span>

                  <ArrowUp size={15} />
                </button>
              ))}
            </div>

          </div>
        )}


        {messages.map((message, index) => (
          <div key={index}>

            {message.role === 'user' ? (
              <UserMessage message={message} />
            ) : (
              <AssistantMessage message={message} />
            )}

          </div>
        ))}


        {busy && (
          <div className="chat-message assistant">

            <span className="message-avatar">
              <Bot size={17} />
            </span>

            <div className="thinking">
              <LoaderCircle
                className="spinner"
                size={16}
              />

              Checking your business records...
            </div>

          </div>
        )}


        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        <div ref={bottom} />

      </div>


      <div className="chat-composer-wrap">

        <form
          className="chat-composer"
          onSubmit={submit}
        >

          <input
            value={draft}
            onChange={(event) => {
              setDraft(event.target.value);
            }}
            placeholder="Ask about stock, prices, sales..."
            aria-label="Ask Walk & Talk Assistant"
            maxLength={1800}
          />

          <button
            type="submit"
            disabled={busy || !draft.trim()}
            aria-label="Send message"
          >
            {busy ? (
              <LoaderCircle
                className="spinner"
                size={19}
              />
            ) : (
              <ArrowUp size={19} />
            )}
          </button>

        </form>

        <p>
          Read-only assistant · Fictional demo data ·
          Confirm stock before committing to a sale
        </p>

      </div>

    </div>
  );
}
