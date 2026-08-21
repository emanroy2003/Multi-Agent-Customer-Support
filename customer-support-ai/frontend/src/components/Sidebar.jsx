import { useAuth } from "../hooks/useAuth.js";

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNewConversation,
  onDelete,
}) {
  const { user, logout } = useAuth();

  return (
    <aside className="flex h-full w-72 flex-col border-r border-gray-200 bg-white">
      <div className="border-b border-gray-200 p-4">
        <button
          onClick={onNewConversation}
          className="w-full rounded-lg bg-brand-600 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
        >
          + New Conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-2">
        {conversations.length === 0 && (
          <p className="px-2 py-4 text-center text-xs text-gray-400">
            No conversations yet.
          </p>
        )}
        {conversations.map((conv) => (
          <div
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={`group mb-1 flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-sm transition ${
              conv.id === activeId
                ? "bg-brand-50 text-brand-700"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            <span className="truncate">
              {conv.is_escalated && <span className="mr-1">🚩</span>}
              {conv.title}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(conv.id);
              }}
              className="ml-2 hidden text-xs text-gray-400 hover:text-red-500 group-hover:inline"
              title="Delete conversation"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-gray-800">{user?.full_name}</p>
            <p className="truncate text-xs text-gray-400">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="ml-2 shrink-0 text-xs font-medium text-gray-400 hover:text-red-500"
          >
            Log out
          </button>
        </div>
      </div>
    </aside>
  );
}
