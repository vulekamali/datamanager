import React from "react";

function notAvailableMessage() {
  return (
    <div>
      <p className="u-fontStyle u-fontStyle--italic">
        This data is not yet available. Provincial budgets are tabled after the
        national budget has been announced. This is because the national budget
        determines the amount of money each province receives. We expect to be
        able make provincial budget data available by April{" "}
        {new Date().getFullYear()}.
      </p>
      <p>
        {
          "In the meantime you view previous financial years' data by selecting a year at the top of your screen."
        }
      </p>
    </div>
  );
}

function public_entities(linksArray) {
  linksArray.sort((a, b) => {return parseInt(b.amount) - parseInt(a.amount)});
  const totalAmount = linksArray.reduce((acc, curr) => acc + parseInt(curr.amount), 0);
  return (
    <table className="PublicEntitySearch-table">
      <thead>
        <tr>
          <th width="30%">Entity name</th>
          <th>Relevant department</th>
          <th>PFMA</th>
          <th>Expenditure ({linksArray[0].selected_year_slug})</th>
        </tr>
      </thead>
      <tbody>
        {linksArray.map(
          (
            {
              name,
              url_path: url,
              department,
              department_slug,
              department_sphere,
              selected_year_slug,
              pfma,
              amount,
            },
            index
          ) => {
            return (
              <tr className="PublicEntityGroup-item" key={index}>
                <td>
                  <a className="PublicEntityGroup-link" href={url}>
                    {name}
                  </a>
                </td>
                <td>
                  <a
                    className="PublicEntityGroup-link"
                    href={
                      "/" +
                      selected_year_slug +
                      "/" +
                      department_sphere +
                      "/departments/" +
                      department_slug
                    }
                  >
                    {department}
                  </a>
                </td>
                <td>{pfma}</td>
                <td>
                  <div className="PublicEntityGroup-expenditure-outer">
                    <div
                      className="PublicEntityGroup-expenditure-inner"
                      style={{
                        width: (amount / totalAmount) * 100 + "%",
                      }}
                    >
                      <label>
                        {parseInt(amount).toLocaleString("en-ZA", {
                          style: "currency",
                          currency: "ZAR",
                        })}
                      </label>
                    </div>
                  </div>
                </td>
              </tr>
            );
          }
        )}
      </tbody>
    </table>
  );
}

export default function PublicEntityGroup({ linksArray }) {
  return (
    <div>
      <div className="PublicEntityGroup">
        <h3 className="PublicEntityGroup-title">
          {linksArray.length} Public entities match your search
        </h3>
        <div className="PublicEntityGroup-mapWrap">
          <div className="PublicEntityGroup-wrap">
            {public_entities(linksArray)}
          </div>
        </div>
      </div>
    </div>
  );
}
