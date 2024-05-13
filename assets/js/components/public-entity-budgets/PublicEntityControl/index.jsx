import React from "react";
import PseudoSelect from "./../../universal/PseudoSelect/index.jsx";
import functiongroup1s from "./partials/functiongroup1s.json";
import departments from "./partials/departments.json";

export default function PublicEntityGroup({
  changeKeywords,
  updateFilter,
  keywords,
  open,
  functiongroup1,
  department
}) {
  const triggerKeyword = (event) => changeKeywords(event.target.value);
  const updateFunctionGroup1 = (value) => updateFilter("functiongroup1", value);
  const updateDepartment = (value) => updateFilter("department", value);

  return (
    <div className="PublicEntityControls">
      <div className="PublicEntityControls-itemWrap">
        <div className="PublicEntityControls-keywords">
          <input
            className="Input"
            placeholder="Start typing to find a public entity"
            defaultValue={keywords}
            onInput={triggerKeyword}
          />
        </div>
      </div>

      <div className="DeptControls-itemWrap">
        <div className="DeptControls-in">in</div>
        <div className="DeptControls-dropdown">
          <PseudoSelect
            name="functiongroup1"
            open={open === "functiongroup1"}
            items={functiongroup1s}
            changeAction={updateFunctionGroup1}
            selected={functiongroup1}
          />
        </div>
      </div>

      <div className="DeptControls-itemWrap">
        <div className="DeptControls-in"></div>
        <div className="DeptControls-dropdown">
          <PseudoSelect
            name="department"
            open={open === "department"}
            items={departments}
            changeAction={updateDepartment}
            selected={department}
          />
        </div>
      </div>
    </div>
  );
}
