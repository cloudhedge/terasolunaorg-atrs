# ATRS Project Variants

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ATRS - 4 Variants                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│              Configuration Style                                │
│                    │                                            │
│        ┌──────────┴──────────┐                                  │
│        ▼                     ▼                                  │
│   JavaConfig            XMLConfig                               │
│   (Annotations)         (XML files)                             │
│        │                     │                                  │
│        │    View Engine      │                                  │
│    ┌───┴───┐             ┌───┴───┐                              │
│    ▼       ▼             ▼       ▼                              │
│   JSP   Thymeleaf       JSP   Thymeleaf                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Dimensions

| Dimension | Option A | Option B |
|-----------|----------|----------|
| **Config** | `JavaConfig` - Spring config via `@Configuration` annotations | `XMLConfig` - Spring config via XML files |
| **View** | `JSP` - Java Server Pages (`.jsp` files) | `Thymeleaf` - Modern template engine (`.html` files) |

## The 4 Combinations

| Folder | Config | View | Notes |
|--------|--------|------|-------|
| `JavaConfig-JSP/` | Java annotations | JSP | **Recommended** - modern config + legacy views |
| `JavaConfig-Thymeleaf/` | Java annotations | Thymeleaf | Most modern stack |
| `XMLConfig-JSP/` | XML files | JSP | Legacy approach |
| `XMLConfig-Thymeleaf/` | XML files | Thymeleaf | Mixed legacy/modern |

## Why 4 Variants?

This is a **learning/demo app** by TERASOLUNA framework. It demonstrates:
- How to migrate from XML to Java config
- How to migrate from JSP to Thymeleaf
- Same business logic works with different tech choices

**All 4 share identical business logic** - only configuration and view layers differ.
