import React from 'react';


export default function List({ currentPhrase, currentItems }) {

  const buildItems = (letterArrayFn) => {
    return letterArrayFn.map((item) => {
      return (
        <div className="Glossary-item">
          <div className="Glossary-title" dangerouslySetInnerHTML={{ __html: item.phrase }} />
          <div className="Glossary-text" dangerouslySetInnerHTML={{ __html: item.description }} />
        </div>
      );
    });
  };


  const buildSections = (currentItemsFn) => {
    return Object.keys(currentItemsFn).map((letter) => {
      const letterArray = currentItemsFn[letter];

      if (letterArray.length > 0) {
        return (
          <div className="Glossary-section" id={`glossary-item-${letter}`}>
            <div className="Glossary-heading">
              {letter.toUpperCase()}
            </div>
            {buildItems(letterArray)}
          </div>
        );
      }

      return null;
    });
  };


  return (
    <div className="Glossary-list">
      {buildSections(currentItems)}
    </div>
  );
}
