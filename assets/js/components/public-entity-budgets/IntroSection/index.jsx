import React from 'react';


export default function IntroSection({ innerHtml, open, setOpen, parentAction, triggered }) {
  const prompt = (
    <div>
      <div className="IntroSection-fade" />
      <div className="IntroSection-button">
        <button className="Button is-secondary is-inline" onClick={setOpen}>Read More</button>
      </div>
    </div>
  );

  if (triggered) {
    return (
      <div className={`IntroSection-text is-initialised ${open ? ' is-open' : ''}`}>
        <div
          className="IntroSection-content"
          dangerouslySetInnerHTML={{ __html: innerHtml }}
          ref={node => parentAction(node)}
        />
        {open ? null : prompt}
      </div>
    );
  }

  return (
    <div className="IntroSection-text">
      <div
        className="IntroSection-content"
        dangerouslySetInnerHTML={{ __html: innerHtml }}
        ref={node => parentAction(node)}
      />
    </div>
  );
}
