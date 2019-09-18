import { h } from 'preact';
import trimValues from './../../../utilities/js/helpers/trimValues.js';


export default function RevenueMarkup({ items }) {
  const keys = Object.keys(items);

  return (
    <div className="ValueBlocks">
      {
        keys.map((key) => {
          const link = items[key].link;
          const value = items[key].value;
          const Tag = link ? 'a' : 'div';

          return (
            <div className="ValueBlocks-itemWrap">
              <Tag href={link} className={`ValueBlocks-item${link ? ' ValueBlocks-item--link' : ''}`}>
                <div className="ValueBlocks-title">{key}</div>
                { value ? <div className="ValueBlocks-value">R{trimValues(value)}</div> : null }
              </Tag>
            </div>
          );
        })
      }
    </div>
  );
}
