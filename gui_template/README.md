# GUI Template System

A reusable GUI template system extracted from CheckMate Virtue for building professional web applications.

## 🎨 Design System

### Color Scheme
- **Primary**: `#667eea` to `#764ba2` (Gradient)
- **Secondary**: `#28a745` (Success)
- **Warning**: `#ffc107` (Warning)
- **Danger**: `#dc3545` (Error)
- **Dark**: `#343a40` (Navbar)

### Typography
- **Font**: Bootstrap default (system fonts)
- **Icons**: Font Awesome 6.0.0
- **Headings**: Bootstrap display classes

### Components
- **Navigation**: Dark navbar with brand and menu items
- **Cards**: Hover effects with shadows
- **Buttons**: Gradient primary buttons
- **Forms**: Bootstrap form styling
- **Modals**: Bootstrap modal components
- **Tables**: Responsive Bootstrap tables

## 📁 Template Structure

```
gui_template/
├── base.html              # Base template with common elements
├── components/            # Reusable UI components
│   ├── navbar.html       # Navigation component
│   ├── cards.html        # Card components
│   ├── forms.html        # Form components
│   ├── modals.html       # Modal components
│   └── buttons.html      # Button components
├── pages/                # Page templates
│   ├── dashboard.html    # Dashboard page
│   ├── list.html         # List/table page
│   ├── detail.html       # Detail view page
│   └── form.html         # Form page
├── static/               # Static assets
│   ├── css/
│   │   ├── main.css      # Custom styles
│   │   └── components.css # Component styles
│   └── js/
│       ├── main.js       # Main JavaScript
│       └── components.js # Component JavaScript
└── examples/             # Example implementations
    ├── inspection_app/   # CheckMate Virtue example
    └── other_apps/       # Other application examples
```

## 🚀 Quick Start

1. **Copy the template structure** to your new project
2. **Customize the branding** in `base.html`
3. **Extend base template** for your pages
4. **Add your components** using the provided patterns

## 📋 Features

### ✅ Responsive Design
- Mobile-first approach
- Bootstrap 5.1.3 grid system
- Flexible card layouts

### ✅ Interactive Elements
- Hover effects on cards
- Smooth transitions
- Loading states

### ✅ Form Handling
- File uploads with preview
- Camera integration
- Drag and drop support

### ✅ Data Display
- Status badges
- Progress indicators
- Photo galleries

### ✅ Navigation
- Breadcrumb navigation
- Active state indicators
- Mobile-friendly menu

## 🎯 Usage Examples

### Basic Page Structure
```html
{% extends "base.html" %}

{% block title %}Your Page Title{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>Your Content</h2>
    <!-- Your page content here -->
</div>
{% endblock %}
```

### Card Component
```html
{% include "components/cards.html" with context %}
```

### Form Component
```html
{% include "components/forms.html" with context %}
```

## 🔧 Customization

### Branding
- Update colors in `static/css/main.css`
- Change logo in `components/navbar.html`
- Modify typography in base template

### Components
- Add new components in `components/` directory
- Extend existing components as needed
- Maintain consistent styling patterns

### JavaScript
- Add custom functionality in `static/js/main.js`
- Use component-specific scripts in `static/js/components.js`
- Follow the established patterns for consistency

## 📱 Mobile Support

- Touch-friendly buttons and forms
- Responsive image galleries
- Mobile-optimized navigation
- Camera integration for mobile devices

## 🎨 Accessibility

- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- High contrast color options
- Screen reader compatibility

## 🔄 Version History

- **v1.0.0**: Initial template based on CheckMate Virtue
- Extracted from production-ready application
- Tested across multiple browsers and devices 