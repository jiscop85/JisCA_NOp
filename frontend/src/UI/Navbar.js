import { Link, useLocation } from 'react-router-dom';
import { Scan, Camera, Upload, Grid3x3, Activity } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'Home', icon: Activity },
    { path: '/detect', label: 'Detect', icon: Scan },
    { path: '/batch', label: 'Batch', icon: Upload },
    { path: '/gallery', label: 'Gallery', icon: Grid3x3 }
  ];
  
  return (
    <nav className="border-b border-zinc-800 bg-zinc-950/50 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 md:px-12">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-violet-500 rounded-sm flex items-center justify-center">
              <Camera className="w-6 h-6 text-black" />
            </div>
            <span className="font-heading font-bold text-xl tracking-tight text-white">JisCA_NOp</span>
          </Link>
                    <div className="flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={`nav-${item.label.toLowerCase()}`}
                  className={`px-4 py-2 rounded-sm text-sm font-medium tracking-wide transition-all duration-200 flex items-center space-x-2 ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-500 shadow-[0_0_10px_rgba(0,240,255,0.2)]'
                      : 'text-zinc-400 hover:text-white hover:bg-zinc-900/50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

