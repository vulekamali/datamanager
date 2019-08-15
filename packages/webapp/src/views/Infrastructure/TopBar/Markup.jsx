import React from 'react';
import styled from 'styled-components';
import SpeedDial from '@material-ui/lab/SpeedDial';
import SpeedDialAction from '@material-ui/lab/SpeedDialAction';
import Button from '@material-ui/core/Button';
import ShareIcon from '@material-ui/icons/Share';
import CloseIcon from '@material-ui/icons/Close';
import LeftIcon from '@material-ui/icons/KeyboardArrowLeft';
import RightIcon from '@material-ui/icons/KeyboardArrowRight';
import { Typography } from '@material-ui/core'
import { darken } from 'polished';
import Modal from './Modal';
import Icon from './Icon';

const StyledSpeedDial = styled(SpeedDial)`
  height: 20px;
  align-self: flex-start;
  margin-right: 4px;

  & .fab {
    background: #C4C4C4;
    width: 36px;
    margin-left: 10px;

    &:hover {
      background: ${darken(0.1, '#C4C4C4')};
    }
  }
`;

const WhiteButton = styled(Button)`
  &&& {
    background: white;
    border-radius: 50px;
    ${({ text }) => (!!text ? 'min-width: 96px' : 'min-width: 36px')};
    ${({ text }) => (!!text ? '' : 'width: 36px')};
    ${({ text }) => (!!text ? 'height: 36px' : 'height: 36px')};
    color: black;
    text-transform: none;
    font-family: Lato;
    font-size: 16px;
    font-weight: 700;
    box-shadow: none;
    opacity: ${({ disabled }) => (disabled ? 0.2 : 1)};
    margin-right: 4px;
    margin-left: 4px;
    ${({ text }) => (!!text ? 'padding-top: 4px ' : '')};
    ${({ text }) => (!!text ? 'padding-right: 25px' : '')};
    padding: 0;
    
    &:hover {
      background: ${darken(0.1, 'white')};
    }
  }
`;

const TwoArrowButtons = styled.div`
  display: flex;
`;

const ButtonsOnTheLeft = styled.div`
  display: flex;
`;

const ButtonsOnTheLeftDetailsFalse = styled.div`
  display: flex;
  padding-bottom: 15px;
`;

const PositionedShareIcon = styled(ShareIcon)`
  position: relative;
  right: 2px;
  color: #3f3f3f;
`;

const StyledCloseIcon = styled(CloseIcon)`
  color: #3f3f3f;
`;

const TextContainer = styled.div`
  display: none;

  @media screen and (min-width: 450px) {
    display: block;
  }
`;

const WhiteText = styled(Typography)`
  text-transform: uppercase;
  max-width: 272px;
  text-align: center;

  && {
    color: #3F3F3F;
    font-family: Lato;
    font-size: 10px;
    font-weight: 700;
    line-height: 16px;
    letter-spacing: 3px;

    @media screen and (min-width: 650px) {
      color: #fff;
      max-width: none;
      line-height: normal;
      font-weight: 400;
      font-size: 14px;
    }
  }
`
const StaticPositionWrapper = styled.div`
  position: sticky;
  top: 0;
  left: 0;
  z-index: 1;
`;

const Wrapper = styled.div`
  position: relative;
  background: #3f3f3f;
  width: 100%;
  height: 60px;
  margin-bottom: 16px;

  @media screen and (min-width: 650px) {
    margin-bottom: 45px;
    margin: 0 auto;
  }
`;

const NavItemsWrapper = styled.div`
  position: relative;
  background: #3f3f3f;
  display: flex;
  width: 100%;
  height: 60px;
  margin-bottom: 80px;
  justify-content: space-between;
  align-items: center;
  padding-right: 16px;
  padding-left: 16px;

  @media screen and (min-width: 450px) {
    margin-bottom: 45px;
    margin: 0 auto;
    max-width: 976px;
  }
`;



const createNewTab = (newUrl) => {
  const { focus } = window.open(newUrl, '_blank');
  return focus();
};

const sharing = [
  'Copy link',
  'Share on Facebook',
  'Share on Twitter',
  'Share on Linkedin',
];


const getUrl = (baseUrl, title) => {
  switch (title) {
    case 'Copy link': return `baseUrl`;
    case 'Share on Facebook': return `https://www.facebook.com/sharer/sharer.php?u=${baseUrl}`;
    case 'Share on Twitter': return `https://twitter.com/home?status=${baseUrl}`;
    case 'Share on Linkedin': return `https://www.linkedin.com/shareArticle?mini=true&url=${baseUrl}`;
    default: return null;
  };
};

const createObjects = (baseUrl, toggleModal, toggleSharingOpen) => (title) => {
  if (title === 'Copy link') {
    return {
      title,
      icon: <Icon {...{ title }} />,
      action: () => {
        toggleSharingOpen();
        toggleModal(baseUrl)
      }
    }
  }

  return {
    title,
    icon: <Icon {...{ title }} />,
    action: () => {
      toggleSharingOpen();
      createNewTab(getUrl(baseUrl, title))
    },
  }
};

const creataShareLink = ({ title, icon, action }) => (
  <SpeedDialAction
    key={title}
    icon={icon}
    tooltipTitle={title}
    onClick={action}
  />
)

const createButtons = (id, toggleModal, toggleSharingOpen) => {
  const baseUrl = id ? `${window.location.href}?id=${id}` : window.location.href;
  const buttonsInfo = sharing.map(createObjects(baseUrl, toggleModal, toggleSharingOpen))

  return buttonsInfo.map(creataShareLink);
};

const createSpeedDial = (sharingOpen, toggleSharingOpen, id, toggleModal) => {
  return (
    <StyledSpeedDial
      ariaLabel="SpeedDial openIcon example"
      icon={!!sharingOpen ? <StyledCloseIcon /> : <PositionedShareIcon />}
      onClick={toggleSharingOpen}
      open={!!sharingOpen}
      direction="down"
      classes={{ fab: 'fab' }}
    >
      {createButtons(id, toggleModal, toggleSharingOpen)}
    </StyledSpeedDial>
  )
}

const buttonMarkup = (disabled, text, reverse, clickEvent) => (
  <WhiteButton variant="contained" {...{ disabled, text }} onClick={clickEvent}>
    {reverse ? <LeftIcon /> : <RightIcon />}
    {!!text && <span>{text}</span>}
  </WhiteButton>
);

const Markup = (props) => {
  const { 
    sharingOpen,
    modal,
    toggleSharingOpen,
    toggleModal,
    amount,
    id,
    details,
    previousId,
    nextId,
    Link = 'a',
  } = props;

  const createWrapperForButtonAndSpeedDial = Link => details ? (
    <ButtonsOnTheLeft>
      {!!details && 
        <Link 
          href="/infrastructure-projects"
          to="/infrastructure-projects"
          style={{ textDecoration: 'none', color: 'black' }}
        >
        {buttonMarkup(false, 'Back', true)}
        </Link>
      }
      {createSpeedDial(sharingOpen, toggleSharingOpen, id, toggleModal)}
    </ButtonsOnTheLeft>
  ) : (
    <ButtonsOnTheLeftDetailsFalse>
      {!!details && buttonMarkup(false, 'Back', true)}
      {createSpeedDial(sharingOpen, toggleSharingOpen, id, toggleModal)}
    </ButtonsOnTheLeftDetailsFalse>
  )

  const whiteTextRendering = details ? (
    <WhiteText>Project Information</WhiteText>
  ) : (
    <WhiteText>{`${amount} national department infrastructure projects`}</WhiteText>
  );

  return (
    <StaticPositionWrapper>
      <Wrapper>
        <NavItemsWrapper>
          <Modal open={!!modal} closeModal={() => toggleModal(null)} url={modal} />
          {createWrapperForButtonAndSpeedDial(Link)}
          <TextContainer>
            {whiteTextRendering}
          </TextContainer>
          <TwoArrowButtons>
            {!details ? buttonMarkup(id <= 0, null, true, previousId) : null}
            {!details ? buttonMarkup(id + 1 >= amount, null, null, nextId) : null}
          </TwoArrowButtons>
        </NavItemsWrapper>
      </Wrapper>
    </StaticPositionWrapper>
  )
}

export default Markup;
