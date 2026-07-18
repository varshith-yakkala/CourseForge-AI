import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import './Breadcrumb.css';

export function Breadcrumb({ customPath }) {
  const location = useLocation();
  const paths = location.pathname.split('/').filter(Boolean);

  // Auto-generate breadcrumbs if customPath isn't provided
  const breadcrumbs = customPath || paths.map((path, index) => {
    const url = `/${paths.slice(0, index + 1).join('/')}`;
    return {
      label: path.charAt(0).toUpperCase() + path.slice(1).replace('-', ' '),
      url
    };
  });

  return (
    <nav className="cf-breadcrumb" aria-label="Breadcrumb">
      <ol className="cf-breadcrumb-list">
        <li className="cf-breadcrumb-item">
          <Link to="/dashboard" className="cf-breadcrumb-link">
            <Home size={14} />
          </Link>
        </li>
        {breadcrumbs.map((bc, idx) => (
          <React.Fragment key={bc.url}>
            <ChevronRight size={14} className="cf-breadcrumb-separator" />
            <li className="cf-breadcrumb-item">
              {idx === breadcrumbs.length - 1 ? (
                <span className="cf-breadcrumb-current" aria-current="page">
                  {bc.label}
                </span>
              ) : (
                <Link to={bc.url} className="cf-breadcrumb-link">
                  {bc.label}
                </Link>
              )}
            </li>
          </React.Fragment>
        ))}
      </ol>
    </nav>
  );
}
