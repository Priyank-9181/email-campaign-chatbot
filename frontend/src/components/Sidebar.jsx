import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Dashboard', icon: '📊' },
  { to: '/datasets', label: 'Datasets', icon: '📦' },
  { to: '/chat', label: 'AI Chat', icon: '🤖' },
  { to: '/campaigns', label: 'Campaigns', icon: '✉️' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 border-r border-slate-200 bg-white p-4 shadow-sm">
      <nav className="flex flex-col gap-2">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/'}
            className={({ isActive }) =>
              `rounded-lg px-3 py-2 text-sm transition ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-indigo-50 hover:text-indigo-700'
              }`
            }
          >
            <span className="mr-2">{link.icon}</span>
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
