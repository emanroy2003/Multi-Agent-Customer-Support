const AGENT_COLORS = {
  billing: "bg-amber-100 text-amber-700",
  technical: "bg-sky-100 text-sky-700",
  product: "bg-violet-100 text-violet-700",
  complaint: "bg-rose-100 text-rose-700",
  faq: "bg-gray-100 text-gray-700",
};

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[75%] ${isUser ? "order-2" : "order-1"}`}>
        {!isUser && message.agents_used?.length > 0 && (
          <div className="mb-1 flex flex-wrap gap-1">
            {message.agents_used.map((agent) => (
              <span
                key={agent}
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  AGENT_COLORS[agent] || "bg-gray-100 text-gray-700"
                }`}
              >
                {agent}
              </span>
            ))}
          </div>
        )}
        <div
          className={`whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm ${
            isUser
              ? "rounded-br-sm bg-brand-600 text-white"
              : "rounded-bl-sm border border-gray-200 bg-white text-gray-800"
          }`}
        >
          {message.content}
        </div>
      </div>
    </div>
  );
}
