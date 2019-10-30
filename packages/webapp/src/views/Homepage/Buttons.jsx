import React from 'react';
import styled from 'styled-components';
import { PrimaryButton, SecondaryButton } from './styled';
import { Link as ScrollLink } from 'react-scroll';


const ButtonsWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;

  @media screen and (min-width: 650px) {
    flex-direction: row;
  }
`;


const LinkWrapper = styled.a`
  display: inline-block;
  padding: 7px;
  text-decoration: none;

  @media screen and (min-width: 650px) {
    padding: 8px;
  }
`;

const ScrollLinkWrapper = styled(ScrollLink)`
  display: inline-block;
  padding: 7px;
  text-decoration: none;

  @media screen and (min-width: 650px) {
    padding: 8px;
  }
`;


const generateLinkProps = link => {
  if (!link) {
    return {};
  }

  return {
    href: link,
    target: '_blank',
    rel: 'noopener noreferrer'
  }
}

const Buttons = ({ primary, secondary }) => (
  <ButtonsWrapper>
    <a href={primary.link} target={primary.target}>
      <PrimaryButton variant="contained">{primary.text}</PrimaryButton>
    </a>
    <a href={secondary.link} target={secondary.target}>
      <SecondaryButton variant="contained">{secondary.text}</SecondaryButton>
    </a>
  </ButtonsWrapper>
);


export default Buttons;


// Buttons.propTypes = {
//   primary: t.shape({
//     text: t.string,
//     link: t.string,
//     clickEvent: t.func,
//   }).isRequired,
//   secondary: t.shape({
//     text: t.string,
//     link: t.string,
//     clickEvent: t.func,
//   }).isRequired,
// };
