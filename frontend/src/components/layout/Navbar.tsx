import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Menu, X, Sprout } from 'lucide-react';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/crop-recommendation', label: 'Crop Recommendation' },
  { to: '/disease-detection', label: 'Disease Detection' },
  { to: '/crops', label: 'Crops' },
  { to: '/history', label: 'History' },
];

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-stone-200/80 bg-white/80 backdrop-blur-lg">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-2.5 text-stone-900 hover:text-emerald-700 transition-colors"
          aria-label="AgriSense Home"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-600 text-white">
            <Sprout className="h-5 w-5" />
          </div>
          <span className="text-lg font-bold tracking-tight">
            Agri<span className="text-emerald-600">Sense</span>
          </span>
        </Link>

        {/* Desktop navigation */}
        <ul className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => (
            <li key={link.to}>
              <NavLink
                to={link.to}
                end={link.to === '/'}
                className={({ isActive }) =>
                  `px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'text-emerald-700 bg-emerald-50'
                      : 'text-stone-600 hover:text-stone-900 hover:bg-stone-50'
                  }`
                }
              >
                {link.label}
              </NavLink>
            </li>
          ))}
        </ul>

        {/* Mobile menu button */}
        <button
          type="button"
          className="md:hidden inline-flex items-center justify-center rounded-lg p-2 text-stone-500 hover:bg-stone-100 hover:text-stone-900 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          onClick={() => setIsOpen(!isOpen)}
          aria-expanded={isOpen}
          aria-label={isOpen ? 'Close menu' : 'Open menu'}
        >
          {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </nav>

      {/* Mobile menu */}
      {isOpen && (
        <div className="md:hidden border-t border-stone-200 bg-white">
          <ul className="px-4 py-3 space-y-1">
            {navLinks.map((link) => (
              <li key={link.to}>
                <NavLink
                  to={link.to}
                  end={link.to === '/'}
                  className={({ isActive }) =>
                    `block px-3 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                      isActive
                        ? 'text-emerald-700 bg-emerald-50'
                        : 'text-stone-600 hover:text-stone-900 hover:bg-stone-50'
                    }`
                  }
                  onClick={() => setIsOpen(false)}
                >
                  {link.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      )}
    </header>
  );
}
