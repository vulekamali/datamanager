import { h } from 'preact';


export default function Controls({ currentPhrase, currentItems, changePhrase }) {
  const buildLetters = () => {
    return Object.keys(currentItems).map((letter) => {
      const hasItems = currentItems[letter].length > 0;

      return (
        <a
          href={`#glossary-item-${letter}`}
          className={`Glossary-letter${hasItems ? ' is-valid' : ''}`}
        >
          {letter.toUpperCase()}
        </a>
      );
    });
  };


  return (
    <div className="Glossary-controls">
      <input
        className="Glossary-search"
        placeholder="Start typing to find a glossary term"
        value={currentPhrase}
        onInput={event => changePhrase(event.target.value)}
      />
      <div className="Glossary-lettersWrap">
        <span className="Glossary-letterLabel">Jump to Letter:</span>
        {buildLetters()}
      </div>
    </div>
  );
}
