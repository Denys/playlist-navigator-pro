import React from 'react';

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
  className?: string;
  title?: string;
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className = '', title, ...props }) => (
  <div
    {...props}
    className={`bg-white/10 backdrop-blur-xl border border-white/20 shadow-xl rounded-3xl p-6 relative overflow-hidden group ${className}`}
  >
    {/* Shine effect on hover */}
    <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/5 to-white/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 ease-in-out pointer-events-none" />
    
    {title && (
      <div className="mb-4 border-b border-white/10 pb-2">
        <h3 className="text-xl font-semibold text-white/90">{title}</h3>
      </div>
    )}
    <div className="relative z-10">
      {children}
    </div>
  </div>
);

export const GlassInput = (props: React.InputHTMLAttributes<HTMLInputElement> & { label?: string; icon?: React.ReactNode }) => (
  <div className="mb-4 w-full">
    {props.label && (
      <label className="block text-sm font-medium text-white/80 mb-2 ml-1 flex items-center gap-2">
        {props.icon}
        {props.label}
      </label>
    )}
    <input
      {...props}
      className={`w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-transparent transition-all backdrop-blur-sm ${props.className}`}
    />
  </div>
);

export const GlassSelect = (props: React.SelectHTMLAttributes<HTMLSelectElement> & { label?: string }) => (
  <div className="mb-4 w-full">
    {props.label && <label className="block text-sm font-medium text-white/80 mb-2 ml-1">{props.label}</label>}
    <div className="relative">
        <select
        {...props}
        className={`w-full appearance-none bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-400/50 transition-all backdrop-blur-sm cursor-pointer ${props.className}`}
        >
        {props.children}
        </select>
        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-white/70">
            <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
        </div>
    </div>
  </div>
);

export const GlassButton = ({ children, variant = 'primary', className = '', ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'secondary' | 'danger' }) => {
  const variants = {
    primary: "bg-gradient-to-r from-purple-600/80 to-blue-600/80 hover:from-purple-500 hover:to-blue-500 text-white shadow-lg shadow-purple-500/20",
    secondary: "bg-white/10 hover:bg-white/20 text-white border border-white/20",
    danger: "bg-red-500/20 hover:bg-red-500/40 text-red-100 border border-red-500/30"
  };

  return (
    <button
      {...props}
      className={`px-6 py-3 rounded-xl font-medium transition-all duration-300 transform active:scale-95 flex items-center justify-center gap-2 backdrop-blur-sm ${variants[variant]} ${className}`}
    >
      {children}
    </button>
  );
};
