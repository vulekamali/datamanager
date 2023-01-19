import PseudoSelect from './../../universal/PseudoSelect/index.jsx';
import provinces from './partials/provinces.json';
import spheres from './partials/spheres.json';


export default function DeptGroup({ changeKeywords, updateFilter, keywords, open, sphere, province }) {
  const triggerKeyword = event => changeKeywords(event.target.value);
  const updateProvince = value => updateFilter('province', value);
  const updateSphere = value => updateFilter('sphere', value);

  return (
    <div className="DeptControls">
      <div className="DeptControls-itemWrap">
        <div className="DeptControls-keywords">
          <input
            className="Input"
            placeholder="Start typing to find a department budget"
            value={keywords}
            onInput={triggerKeyword}
          />
        </div>
      </div>
      <div className="DeptControls-itemWrap">
        <div className="DeptControls-in">in</div>
        <div className="DeptControls-dropdown">
          <PseudoSelect
            name="sphere"
            open={open === 'sphere'}
            items={spheres}
            changeAction={updateSphere}
            selected={sphere}
          />
        </div>
      </div>
      {
        sphere === 'provincial' ?
          <div className="DeptControls-itemWrap">
            <div>
              <div className="DeptControls-in">in</div>
              <div className="DeptControls-dropdown">
                <PseudoSelect
                  name="province"
                  open={open === 'province'}
                  items={provinces}
                  changeAction={updateProvince}
                  selected={province}
                />
              </div>
            </div>
          </div>
          : null
      }

    </div>
  );
}
