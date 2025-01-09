export function setupKeyboardShortcuts(handlers) {
  const handleKeydown = (e) => {
    if (e.ctrlKey || e.metaKey) {
      switch(e.key) {
        case 'b':
          e.preventDefault()
          handlers.applyFormat?.('bold')
          break
        case 'i':
          e.preventDefault()
          handlers.applyFormat?.('italic')
          break
        case 'u':
          e.preventDefault()
          handlers.applyFormat?.('underline')
          break
        case 'z':
          e.preventDefault()
          if (e.shiftKey) {
            handlers.redo?.()
          } else {
            handlers.undo?.()
          }
          break
      }
    }
  }

  document.addEventListener('keydown', handleKeydown)

  return () => {
    document.removeEventListener('keydown', handleKeydown)
  }
} 