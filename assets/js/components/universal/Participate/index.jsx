import React from 'react';
import returnHtml from './partials/returnHtml.js';
import PseudoSelect from './../../universal/PseudoSelect/index.jsx';
import createTooltips from './../../universal/Tooltip/index.js';


export default function Participate({months, selected, setMonth, mobile, open, setMobileMonth}) {

    const selectors = Object.keys(months).map((month, index) => {
        const activeState = selected === month ? ' is-active' : '';

        return (
            <button
                key={index}
                className={`Participate-button${activeState}`}
                onClick={() => setMonth(month)}
            >
                {month}
            </button>
        );
    });

    const mobileSelectors = (
        <PseudoSelect
            items={months}
            selected={selected}
            changeAction={month => setMobileMonth(month)}
            name="participate-select"
            open={open}
        />
    );

    return (
        <div className="Participate">
            {mobile ? mobileSelectors : selectors}
            <div
                className="Participate-info"
                dangerouslySetInnerHTML={{__html: returnHtml(selected)}}
                ref={node => createTooltips([node])}
            />
        </div>
    );
}
