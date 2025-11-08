# SYNTEST - A Synesthesia Testing Framework 


--- 

# CSS For Developers
Please reference the below styling classes and components whenever creating a new page. Note how classes (.container, .card, .flex, ...) are used instead of redefining new styles for each page. Moving forward, we should only need to modify app.css very little, and instead use from its components. 

## CSS Variables (Design Tokens)

| Category | Variable | Value | Usage |
|----------|----------|-------|-------|
| **Colors** | `--color-primary` | `#111` | Primary brand color |
| | `--color-secondary` | `#666` | Secondary brand color |
| | `--color-white` | `#fff` | White |
| | `--color-black` | `#000` | Black |
| **Backgrounds** | `--bg-primary` | `#fff` | Main background |
| | `--bg-secondary` | `#f5f5f5` | Secondary background |
| | `--bg-tertiary` | `#f3f3f3` | Tertiary background |
| | `--bg-light` | `#fafafa` | Light background |
| **Borders** | `--border-primary` | `#e5e7eb` | Primary border |
| | `--border-secondary` | `#ececec` | Secondary border |
| | `--border-medium` | `#cccccc` | Medium border |
| **Text** | `--text-primary` | `#111` | Primary text |
| | `--text-secondary` | `#666` | Secondary text |
| | `--text-muted` | `#6b7280` | Muted text |
| | `--text-inverse` | `#fff` | Inverse text (for dark backgrounds) |
| **Semantic** | `--color-error` | `#ff0000` | Error states |
| | `--color-success` | `#4caf50` | Success states |
| | `--color-info` | `#3046d6` | Info states |
| | `--color-warning` | `#ffb020` | Warning states |
| **Shadows** | `--shadow-xs` to `--shadow-xl` | Various | Elevation shadows |
| **Typography** | `--font-size-xs` to `--font-size-5xl` | `12px` to `48px` | Font sizes |
| | `--line-height-tight` to `--line-height-loose` | `1.25` to `1.6` | Line heights |
| **Spacing** | `--spacing-xs` to `--spacing-5xl` | `4px` to `48px` | Consistent spacing |
| **Radius** | `--radius-sm` to `--radius-full` | `0px` to `0px` | Border radius (currently flat design) |
| **Transitions** | `--transition-fast/base/slow` | `0.15s` to `0.3s` | Animation timing |

---

## Layout Components

### Container System
| Class | Max Width | Usage | Used In |
|-------|-----------|-------|---------|
| `.container` | `1200px` | Standard content width | All templates |
| `.container-sm` | `600px` | Narrow content | Forms, auth pages |
| `.container-md` | `900px` | Medium content | `screen_flow.html` |
| `.container-lg` | `1400px` | Wide content | Dashboard wide views |
| `.container-fluid` | `100%` | Full width | - |
| `.container-centered` | - | Vertically & horizontally centered | Landing pages |

### Navigation
| Class | Purpose | Used In |
|-------|---------|---------|
| `.topbar` | Sticky top navigation bar | `base.html`, all templates |
| `.brand` | Logo/brand text styling | `base.html`, `dashboard.html` |
| `.nav` | Horizontal navigation container | `base.html` |
| `.nav-link` | Navigation link styling | `base.html` |
| `.side-nav` | Vertical sidebar navigation | `dashboard.html` |
| `.nav-item` | Sidebar navigation item | `dashboard.html` |
| `.nav-item.active` | Active nav state | Dynamic |

### Layout Helpers
| Class | Purpose | Used In |
|-------|---------|---------|
| `.shell` | Flexbox container for centered content | Color test templates |
| `.content` | Main content wrapper with card styling | Color test templates |
| `.panel` | Full-width background section | Future use |

---

## Typography

### Headings
| Element/Class | Font Size | Font Weight | Used In |
|--------------|-----------|-------------|---------|
| `h1` | `clamp(32px, 5vw, 48px)` | `800` | Page titles |
| `h2` | `clamp(24px, 3vw, 28px)` | `700` | Section titles |
| `h3` | `20px` | `700` | Subsections |
| `h4` | `18px` | `700` | Card titles |
| `h5`, `h6` | `16px` | `700` | Small headings |

### Text Utilities
| Class | Purpose | Used In |
|-------|---------|---------|
| `.lead` | Larger intro text | `screen_flow.html`, color tests |
| `.text-muted` | Muted/secondary text | Forms, help text |
| `.text-small` | Small text (`12px`) | Captions |
| `.caption` | Centered caption text | Color test templates |
| `.label-uppercase` | Small uppercase labels | `screen_flow.html` |
| `.prompt` | Large centered prompt text | Future use |

---

## Button System

### Button Variants
| Class | Background | Border | Shadow | Used In |
|-------|-----------|--------|--------|---------|
| `.btn-primary` | Black | None | Large | Primary actions (all templates) |
| `.btn-secondary` | White | Gray | XS | Secondary actions (`screen_flow.html`) |
| `.btn-ghost` | Light gray | Gray | None | Tertiary actions (`dashboard.html`) |

### Button Sizes
| Class | Padding | Font Size | Used In |
|-------|---------|-----------|---------|
| `.btn-sm` | `8px 14px` | `14px` | `base.html` (Help button) |
| `.btn-md` | `12px 18px` | `16px` | Standard buttons |
| `.btn-lg` | `14px 22px` | `18px` | Primary CTAs |
| `.btn-xl` | `16px 28px` | `20px` | Hero buttons |

### Button Modifiers
| Class | Purpose | Used In |
|-------|---------|---------|
| `.btn-block` | Full width button | `screen_flow.html` |
| `.btn-icon` | Button with icon spacing | Future use |
| `.btn:disabled` | Disabled state | Color tests |

---

## Card System

| Class | Purpose | Used In |
|-------|---------|---------|
| `.card` | Standard card container | All templates |
| `.card-sm` | Smaller padding | - |
| `.card-lg` | Larger padding | - |
| `.card-header` | Card header with bottom border | Color tests |
| `.card-title` | Card title styling | Color tests, `screen_flow.html` |
| `.card-body` | Card body content | - |
| `.card-footer` | Card footer with top border | - |

---

## Form Components

### Input Fields
| Selector | Styling | Used In |
|----------|---------|---------|
| `input[type="text"]`, `input[type="email"]`, etc. | Standard input styling | Forms throughout app |
| `input:focus` | Focus state (black border) | All inputs |
| `input:disabled` | Disabled state | Forms |
| `select`, `textarea` | Same as inputs | Forms |

### Checkbox/Radio
| Class | Purpose | Used In |
|-------|---------|---------|
| `.checkbox-group` | Checkbox with label layout | `screen_flow.html` |
| `.radio-group` | Radio with label layout | - |
| `.select-card` | Radio inside card UI | `screen_flow.html` (Step 3) |
| `.select-list` | Container for select cards | `screen_flow.html` |

### Type Selection (Screening)
| Class | Purpose | Used In |
|-------|---------|---------|
| `.type-rows` | Container for type options | `screen_flow.html` (Step 4) |
| `.type-row` | Single type option row | `screen_flow.html` |
| `.type-main` | Type title/description | `screen_flow.html` |
| `.type-opts` | Yes/Sometimes/No options | `screen_flow.html` |
| `.opt` | Individual option with underline | `screen_flow.html` |
| `.other-input` | "Other" text input | `screen_flow.html` |

---

## Badge & Tag System

### Chips
| Class | Background | Text Color | Used In |
|-------|-----------|-----------|---------|
| `.chip-primary` | `#eaf0ff` | `#3046d6` | `screen_flow.html` |
| `.chip-success` | `#e9f7ef` | `#177a49` | `screen_flow.html` |
| `.chip-info` | `#e7efff` | `#2b50ff` | `screen_flow.html` |
| `.chip-warning` | `#fff8e1` | `#b8860b` | - |

### Tags
| Class | Purpose | Used In |
|-------|---------|---------|
| `.tag` | Simple tag badge | `screen_flow.html` (Step 5) |
| `.tag-group` | Tag container with wrapping | `screen_flow.html` |

---

## Alert System

| Class | Background | Border | Text | Used In |
|-------|-----------|--------|------|---------|
| `.alert-error` | `#ffebee` | Red | `#c62828` | Error messages |
| `.alert-success` | `#e8f5e9` | Green | `#2e7d32` | Success messages |
| `.alert-info` | Gray | Gray | Black | Info messages |
| `.alert-warning` | `#fff8e1` | Orange | `#f57c00` | Warnings |

Used in: `base.html` (flash messages), color tests (noscript)

---

## Progress Components

| Class | Purpose | Used In |
|-------|---------|---------|
| `.progress` | Progress container | `screen_flow.html` |
| `.progress-top` | Label row (Step X of Y, percentage) | `screen_flow.html` |
| `.progress-track` | Progress bar track | `screen_flow.html` |
| `.progress-bar` | Filled progress indicator | `screen_flow.html` |
| `.status` | Status row (Item, Trial, Progress) | Color tests |
| `.status-badge` | Badge for status display | - |

---

## Grid & Layout Utilities

### Grid System
| Class | Columns | Gap | Used In |
|-------|---------|-----|---------|
| `.grid-2` | 2 columns | `var(--spacing-xl)` | `screen_flow.html` (Step 2) |
| `.grid-3` | 3 columns | `var(--spacing-xl)` | - |
| `.grid-4` | 4 columns | `var(--spacing-xl)` | - |
| `.grid-auto` | Auto-fit (`minmax(200px, 1fr)`) | `var(--spacing-xl)` | - |

### Flexbox Utilities
| Class | Purpose | Used In |
|-------|---------|---------|
| `.flex` | Display flex | Throughout |
| `.flex-col` | Flex direction column | `dashboard.html` |
| `.flex-row` | Flex direction row | `dashboard.html` |
| `.flex-center` | Center items (both axes) | - |
| `.flex-between` | Space between | Multiple |
| `.flex-gap-sm` | `8px` gap | `dashboard.html` |
| `.flex-gap-md` | `12px` gap | - |
| `.flex-gap-lg` | `20px` gap | - |

---

## Choice Cards (Screening Step 2)

| Class | Purpose | Used In |
|-------|---------|---------|
| `.choice-grid` | 2-column grid for choices | `screen_flow.html` |
| `.choice-card` | Individual choice card | `screen_flow.html` |
| `.choice-title` | Choice title | `screen_flow.html` |
| `.choice-subtitle` | Choice description | `screen_flow.html` |
| `.choice-negative` | Full-width negative option (dark) | `screen_flow.html` |
| `.selected` | Selected state (2px border, scale) | Dynamic JS |

---

## Info Panels

| Class | Purpose | Used In |
|-------|---------|---------|
| `.info-panel` | Light blue info box | `screen_flow.html` (Step 3) |
| `.info-rows` | List container for info rows | `screen_flow.html` |
| `.i` | Icon container | `screen_flow.html` |
| `.i.bolt` | Lightning bolt icon (⚡) | `screen_flow.html` |
| `.i.heart` | Heart icon (❤) | `screen_flow.html` |
| `.i.dot` | Dot indicator | `screen_flow.html` |
| `.note-panel` | Gray note box | - |

---

## List Styles

| Class | Purpose | Used In |
|-------|---------|---------|
| `.list-unstyled` | Remove default list styling | - |
| `.list-spaced` | Add bottom margin to `<li>` | Color tests (help dialog) |
| `.list-icon` | List with icon spacing | - |
| `.arrow-list` | List with arrow (➜) bullets | `screen_flow.html` |
| `.plain-list` | Plain list, no bullets | `screen_flow.html` |

---

## Table Components

| Class | Styling | Used In |
|-------|---------|---------|
| `.table` | Full-width bordered table | - |
| `.table th` | Black header | - |
| `.table tr:nth-child(even)` | Striped rows | - |

---

## Summary Components (Step 5)

| Class | Purpose | Used In |
|-------|---------|---------|
| `.summary` | Summary container | `screen_flow.html`, color tests |
| `.summary.hidden` | Hidden state | Dynamic |
| `.summary-grid` | 3-column grid | `screen_flow.html` |
| `.summary-card` | Individual summary card | `screen_flow.html` |
| `.summary-title` | Summary card title | `screen_flow.html` |
| `.summary-sub` | Summary card subtitle | `screen_flow.html` |
| `.summary-list` | List inside summary | `screen_flow.html` |
| `.summary-note` | Note box in summary | `screen_flow.html` |

---

## Action Buttons Container

| Class | Purpose | Used In |
|-------|---------|---------|
| `.actions` | Button container with gap | All templates |
| `.actions-between` | Space between buttons | `screen_flow.html` |
| `.actions-center` | Center buttons | Color tests |
| `.actions-end` | Right-align buttons | Help dialogs |

---

## Auth Components

| Class | Purpose | Used In |
|-------|---------|---------|
| `.role-selector` | 2-column grid for roles | Auth pages |
| `.role-card` | Role selection card | Auth pages |
| `.role-card.active` | Selected role state | Auth pages |

---

## Utility Classes

### Text Alignment
| Class | Purpose |
|-------|---------|
| `.text-left` | Left align |
| `.text-center` | Center align |
| `.text-right` | Right align |

### Font Weight
| Class | Weight |
|-------|--------|
| `.font-normal` | `400` |
| `.font-medium` | `500` |
| `.font-semibold` | `600` |
| `.font-bold` | `700` |
| `.font-extrabold` | `800` |

### Text Transform
| Class | Purpose |
|-------|---------|
| `.uppercase` | Uppercase |
| `.lowercase` | Lowercase |
| `.capitalize` | Capitalize |

### Display
| Class | Display Value |
|-------|--------------|
| `.hidden` | `none !important` |
| `.block` | `block` |
| `.inline-block` | `inline-block` |
| `.flex` | `flex` |
| `.inline-flex` | `inline-flex` |
| `.grid` | `grid` |

### Spacing (Margin)
| Class | Value | Notes |
|-------|-------|-------|
| `.m-0` to `.m-5` | `0` to `var(--spacing-2xl)` | All sides |
| `.mt-0` to `.mt-5` | `0` to `var(--spacing-2xl)` | Top |
| `.mr-0` to `.mr-5` | `0` to `var(--spacing-2xl)` | Right |
| `.mb-0` to `.mb-5` | `0` to `var(--spacing-2xl)` | Bottom |
| `.ml-0` to `.ml-5` | `0` to `var(--spacing-2xl)` | Left |

### Spacing (Padding)
| Class | Value | Notes |
|-------|-------|-------|
| `.p-0` to `.p-5` | `0` to `var(--spacing-2xl)` | All sides |
| `.pt-0` to `.pt-5` | `0` to `var(--spacing-2xl)` | Top |
| `.pr-0` to `.pr-5` | `0` to `var(--spacing-2xl)` | Right |
| `.pb-0` to `.pb-5` | `0` to `var(--spacing-2xl)` | Bottom |
| `.pl-0` to `.pl-5` | `0` to `var(--spacing-2xl)` | Left |

### Width
| Class | Value |
|-------|-------|
| `.w-full` | `100%` |
| `.w-auto` | `auto` |

