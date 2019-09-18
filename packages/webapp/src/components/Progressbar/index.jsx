import React from 'react';
import styled from 'styled-components';
import LinearProgress from '@material-ui/core/LinearProgress';

const calcProgress = (name) => {
  const increment = 100 / 9;

  switch (name) {
    case 'Site identification': return increment * 1;
    case 'Pre-feasibility': return increment * 2;
    case 'Feasibility': return increment * 3;
    case 'Design': return increment * 4;
    case 'Tender': return increment * 5;
    case 'Construction': return increment * 6;
    case 'Hand over': return increment * 7;
    case 'Handed over': return increment * 8;
    case 'Complete': return increment * 9;
    default: return null;
  }
}

const StyledLinearProgress = styled(LinearProgress)`
  && {
    height: 16px;
    border-radius: 200px;
    background: #dcdcdc;

    & .barColorPrimary {
      background: linear-gradient(90deg, rgba(255, 255, 255, 0.8) 0%, #eca03e 83.33%), #eca03e;
      border-right: 2px solid;
    }
  }
`;

const Progressbar = ({ stage }) => {
  if (!stage) return null;

  return (
    <React.Fragment>
      <StyledLinearProgress
        classes={{barColorPrimary: 'barColorPrimary'}}
        variant="determinate"
        value={calcProgress(stage)} />
    </React.Fragment>
  );
};

// Progressbar.propTypes = {
//   /* string that determines how far the progress should be on the progressbar. */
//   stage: t.oneOf([
//     'Site identification',
//     'Pre-feasibility',
//     'Feasibility',
//     'Design',
//     'Tender',
//     'Construction',
//     'Hand over',
//     'Handed over',
//     'Complete'])
// }

// Progressbar.defaultProps = {
//   stage: null
// }

export default Progressbar;
