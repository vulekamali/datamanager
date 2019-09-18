import styled from 'styled-components';

const StyledCircle = styled.circle`
  stroke: #000000;
`;

const StyledSvg = styled.svg`
  border: 0.5px solid #000000;
  border-radius: 50%;
  margin-right: 12px;
  width: 20px;
  height: 20px;
  
  @media screen and (min-width: 900px) {
    width: 40px;
    height: 40px;
  }
`;

export {
  StyledCircle,
  StyledSvg,
}
