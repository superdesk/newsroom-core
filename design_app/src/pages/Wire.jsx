import React from 'react';
import Toggle from 'react-toggle';
import classNames from 'classnames';
import 'react-toggle/style.css';
import {useState} from 'react';
import AdvancedSearch from '../components/AdvancedSearch';
import AdvancedSearchTips from '../components/AdvancedSearchTips';
//import { useNavigate } from 'react-router-dom';

function Wire() { 

    const [isTagSectionShown, setIsTagSectionShown] = useState(false);    
    const handleClickTag = event => {
        setIsTagSectionShown(current => !current);
    };
    const [isAdvancedSearchShown, setIsAdvancedSearchShown] = useState(false);
    const handleClickAdvancedSearch = event => {
        setIsAdvancedSearchShown(current => !current);
    };
    const [isAdvancedSearchTipsShown, setIsAdvancedSearchTipsShown] = useState(false);
    const handleClickAdvancedSearchTips = event => {
        setIsAdvancedSearchTipsShown(current => !current);
    };

    const [state, setState] = useState('red');
    const colorHandler = () => {
            setState(state === 'red' ? 'blue' : 'red');
    };

    const [isMyTopicsShown, setIsMyTopicsShown] = useState(true);
    const [isCompanyTopicsShown, setIsCompanyTopicsShown] = useState(false);
    const handleClickMyTopics = event => {
        setIsMyTopicsShown(current => !current);
    };
    const handleClickCompanyTopics = event => {
        setIsCompanyTopicsShown(current => !current);
    };

    const [isTopicFolderOneOpen, setIsTopicFolderOneOpen] = useState(true);
    const [isTopicFolderTwoOpen, setIsTopicFolderTwoOpen] = useState(true);
    const [isTopicFolderThreeOpen, setIsTopicFolderThreeOpen] = useState(false);
    const handleClickFolderOne = event => {
        setIsTopicFolderOneOpen(current => !current);
    };
    const handleClickFolderTwo = event => {
        setIsTopicFolderTwoOpen(current => !current);
    };
    const handleClickFolderThree = event => {
        setIsTopicFolderThreeOpen(current => !current);
    };








    return (
        <div className="wire-wrap">
            <div className="content">
                <section className="content-header">
                    <h3 className="a11y-only">Wire Content</h3>
                    <nav className="content-bar navbar justify-content-start flex-nowrap flex-sm-wrap">
                        <button className="content-bar__menu content-bar__menu--nav" title="" aria-label="Open filter panel" data-original-title="Open filter panel"><i className="icon--hamburger"></i></button>
                        {/* Search */}
                        <div className="search">
                            <form className="search__form search__form--active" role="search" aria-label="search">
                                <input
                                    type='text'
                                    name='q'
                                    className='search__input form-control'
                                    placeholder="Search for..."
                                    aria-label="Search for..."
                                />
                                <div className='search__form-buttons'>
                                    <button className='search__button-clear' aria-label="Clear search" type="reset">
                                        <svg fill="none" height="18" viewBox="0 0 18 18" width="18" xmlns="http://www.w3.org/2000/svg">
                                            <path clip-rule="evenodd" d="m9 18c4.9706 0 9-4.0294 9-9 0-4.97056-4.0294-9-9-9-4.97056 0-9 4.02944-9 9 0 4.9706 4.02944 9 9 9zm4.9884-12.58679-3.571 3.57514 3.5826 3.58675-1.4126 1.4143-3.58252-3.5868-3.59233 3.5965-1.41255-1.4142 3.59234-3.59655-3.54174-3.54592 1.41254-1.41422 3.54174 3.54593 3.57092-3.57515z" fill="var(--color-text)" fill-rule="evenodd" opacity="1"/>
                                        </svg>
                                    </button>
                                    <button className='search__button-submit' type='submit' aria-label="Search">
                                        <i className="icon--search"></i>
                                    </button>
                                </div>
                            </form>
                        </div>
                        <div className="mx-2 d-flex gap-2">
                            <button onClick={handleClickAdvancedSearch} className="nh-button nh-button--secondary" >Advanced Search</button>
                            <button onClick={handleClickAdvancedSearchTips} className="icon-button icon-button--tertiary icon-button--bordered" aria-label="Info"><i className="icon--info"></i></button>
                        </div>                     
                    </nav>
                </section>
                <section className="content-main">
                    <div className="wire-column--3">
                    <div className="wire-column__nav wire-column__nav--open">
                        <h3 className="a11y-only">Side filter panel</h3>
                        <div className="wire-column__nav__items">
                            <ul className="nav" id="pills-tab" role="tablist">
                                <li className="wire-column__nav__tab nav-item">
                                    <a className="nav-link false" role="tab" aria-selected="false" aria-label="Topics" href="">Topics</a>
                                </li>
                                <li className="wire-column__nav__tab nav-item">
                                    <a className="nav-link active" role="tab" aria-selected="true" aria-label="My Topics" href="">My Topics</a>
                                </li>
                                <li className="wire-column__nav__tab nav-item">
                                    <a className="nav-link false" role="tab" aria-selected="false" aria-label="Filters" href="">Filters</a>
                                </li>
                            </ul>
                            <div className="tab-content ">
                                <div className="filter-panel__topics-list">

                                     {/* My topics */}
                                    <div className={`nh-collapsible-panel pt-0 nh-collapsible-panel--small ${isMyTopicsShown ? 'nh-collapsible-panel--open' : 'nh-collapsible-panel--closed'}`}>
                                        <div className="nh-collapsible-panel__header">
                                            <div className='nh-collapsible-panel__button' role='button' onClick={handleClickMyTopics}>
                                                <div className="nh-collapsible-panel__caret">
                                                    <i className="icon--arrow-right"></i>
                                                </div>
                                                <h3 className='nh-collapsible-panel__title'>My Topics</h3>
                                            </div>
                                            <div className='nh-collapsible-panel__line'></div>
                                            <button className='nh-button nh-button--tertiary nh-button--small'>Edit</button>
                                        </div>

                                        <div className='nh-collapsible-panel__content-wraper'>
                                            <div className='nh-collapsible-panel__content'>
                                                <div className={`collapsible-box collapsible-box--active-within ${isTopicFolderOneOpen ? 'collapsible-box--open' : 'collapsible-box--closed'}`}>
                                                    <div className="collapsible-box__header" onClick={handleClickFolderOne} role='button'>
                                                        <h4 className="collapsible-box__header-title">Politics Topic Folder</h4>
                                                        <div className="collapsible-box__header-caret">
                                                            <i className="icon--arrow-start"></i>
                                                        </div>
                                                    </div>
                                                    <div className="collapsible-box__content">
                                                        <ul className="topic-list">
                                                            <li className="topic-list__item">
                                                                <a className="topic-list__item-link" aria-selected="false" href="">
                                                                    <span className="topic-list__item-link_label">Ontario</span>
                                                                    <span className="badge rounded-pill bg-info">4</span>
                                                                </a>
                                                            </li>
                                                            <li className="topic-list__item">
                                                                <a className="topic-list__item-link" aria-selected="false" href="">
                                                                    <span className="topic-list__item-link_label">Donald Trump</span>
                                                                </a>
                                                            </li>
                                                            <li className="topic-list__item">
                                                                <a className="topic-list__item-link" aria-selected="false" href="">
                                                                    <span className="topic-list__item-link_label">Rishi Sunak</span>
                                                                </a>
                                                            </li>
                                                            <li className="topic-list__item">
                                                                <a className="topic-list__item-link topic-list__item-link--active" aria-selected="true" href="">
                                                                    <span className="topic-list__item-link_label">Donetsk (testing active state)</span>
                                                                    <span className="badge rounded-pill bg-info">8</span>
                                                                </a>
                                                            </li>
                                                        </ul>
                                                    </div>
                                                </div>

                                                <div className={`collapsible-box ${isTopicFolderTwoOpen ? 'collapsible-box--open' : 'collapsible-box--closed'}`}>
                                                    <div className="collapsible-box__header" onClick={handleClickFolderTwo} role='button'>
                                                        <h4 className="collapsible-box__header-title">Culture Topic folder</h4>
                                                        <div className="collapsible-box__header-caret">
                                                            <i className="icon--arrow-start"></i>
                                                        </div>
                                                    </div>
                                                    <div className="collapsible-box__content">
                                                    <ul className="topic-list">
                                                            <li className="topic-list__item">
                                                                <a className="topic-list__item-link" aria-selected="false" href="">
                                                                    <span className="topic-list__item-link_label">My Culture Topic one</span>
                                                                    <span className="badge rounded-pill bg-info">2</span>
                                                                </a>
                                                            </li>
                                                            <li className="topic-list__item">
                                                                <a className="topic-list__item-link" aria-selected="false" href="">
                                                                    <span className="topic-list__item-link_label">My Culture Topic two</span>
                                                                </a>
                                                            </li>
                                                            <li className="topic-list__item">
                                                                <a className="topic-list__item-link" aria-selected="false" href="">
                                                                    <span className="topic-list__item-link_label">My Culture Topic three</span>
                                                                </a>
                                                            </li>
                                                        </ul>
                                                    
                                                    </div>
                                                </div>
                                                <ul className="topic-list topic-list--unsorted">
                                                    <li className="topic-list__item">
                                                        <a className="topic-list__item-link" aria-selected="false" href="">
                                                            <span className="topic-list__item-link_label">Ontario</span>
                                                            <span className="badge rounded-pill bg-info">4</span>
                                                        </a>
                                                    </li>
                                                    <li className="topic-list__item">
                                                        <a className="topic-list__item-link" aria-selected="false" href="">
                                                            <span className="topic-list__item-link_label">Donald Trump</span>
                                                        </a>
                                                    </li>
                                                    <li className="topic-list__item">
                                                        <a className="topic-list__item-link" aria-selected="false" href="">
                                                            <span className="topic-list__item-link_label">Rishi Sunak</span>
                                                        </a>
                                                    </li>
                                                    <li className="topic-list__item">
                                                        <a className="topic-list__item-link" aria-selected="false" href="">
                                                            <span className="topic-list__item-link_label">Donetsk</span>
                                                            <span className="badge rounded-pill bg-info">8</span>
                                                        </a>
                                                    </li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>


                                    {/* Company topics */}

                                    <div className={`nh-collapsible-panel nh-collapsible-panel--small ${isCompanyTopicsShown ? 'nh-collapsible-panel--open' : 'nh-collapsible-panel--closed'}`}>
                                        <div className="nh-collapsible-panel__header">
                                            <div className='nh-collapsible-panel__button' role='button' onClick={handleClickCompanyTopics}>
                                                <div className="nh-collapsible-panel__caret">
                                                    <i className="icon--arrow-right"></i>
                                                </div>
                                                <h3 className='nh-collapsible-panel__title'>Company Topics</h3>
                                            </div>
                                            <div className='nh-collapsible-panel__line'></div>
                                            <button className='nh-button nh-button--tertiary nh-button--small'>Edit</button>
                                        </div>

                                        <div className='nh-collapsible-panel__content-wraper'>
                                            <div className='nh-collapsible-panel__content'>
                                                <div className={`collapsible-box ${isTopicFolderThreeOpen ? 'collapsible-box--open' : 'collapsible-box--closed'}`}>
                                                    <div className="collapsible-box__header" onClick={handleClickFolderThree} role='button'>
                                                        <h4 className="collapsible-box__header-title">Company Topic folder</h4>
                                                        <div className="collapsible-box__header-caret">
                                                            <i className="icon--arrow-start"></i>
                                                        </div>
                                                    </div>
                                                    <div className="collapsible-box__content">
                                                    
                                                    </div>
                                                </div>
                                                <ul className="topic-list topic-list--unsorted">
                                                    <li className="topic-list__item">
                                                        <a className="topic-list__item-link topic-list__item-link--active" aria-selected="false" href="">
                                                            <span className="topic-list__item-link_label">Ontario (testing active state)</span>
                                                            <span className="badge rounded-pill bg-info">2</span>
                                                        </a>
                                                    </li>
                                                    <li className="topic-list__item">
                                                        <a className="topic-list__item-link" aria-selected="false" href="">
                                                            <span className="topic-list__item-link_label">Donald Trump</span>
                                                        </a>
                                                    </li>
                                                    <li className="topic-list__item">
                                                        <a className="topic-list__item-link" aria-selected="false" href="">
                                                            <span className="topic-list__item-link_label">Rishi Sunak</span>
                                                        </a>
                                                    </li>
                                                </ul>
                                            </div> 
                                        </div>

                                    </div>

                                </div>
                            </div>
                        </div>
                    </div>
                        <div className="wire-column__main">
                            <div className="wire-column__main-header-container">
                                <div className="navbar navbar--flex line-shadow-end--light">
                                    <div className="search-result-count">12,339 results</div>
                                    <div className="navbar__button-group">
                                        <button className="nh-button nh-button--tertiary">Clear all</button>
                                        <button onClick={handleClickTag} className="icon-button icon-button--tertiary icon-button--bordered">
                                            {isTagSectionShown && <i className="icon--arrow-right icon--collapsible-open"></i>}
                                            {!isTagSectionShown && <i className="icon--arrow-right icon--collapsible-closed"></i>}
                                        </button>
                                    </div>
                                </div>
                                {isTagSectionShown &&
                                    <div className="navbar navbar--flex line-shadow-end--light navbar--auto-height">
                                        <ul className="search-result__tags-list">
                                            
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Topic</span>
                                                <div className="tags-list">
                                                    <span className="tag-label tag-label--inverse">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">My Ukraine War Topic</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                </div>
                                                <div className="tags-list-row__button-group">
                                                    <button className="nh-button nh-button--tertiary nh-button--small">Update topic</button>
                                                    <button className="nh-button nh-button--tertiary nh-button--small">Save as new topic</button>
                                                </div>
                                            </li>

                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Searched for</span>
                                                <div className="tags-list">
                                                    <span className="tag-label">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">Donetsk</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                </div>
                                            </li>

                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Searched for</span>
                                                <div className="tags-list">
                                                <span className="tag-label tag-label--operator tag-label--success">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">and</span>
                                                        </span>
                                                    </span>
                                                    <span className="tag-label tag-label--success">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">Russia</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--success">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">War</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>

                                                    <span className="tag-list__separator"></span>

                                                    <span className="tag-label tag-label--operator tag-label--info">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">or</span>
                                                        </span>
                                                    </span>
                                                    <span className="tag-label tag-label--info">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">Zelensky</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--info">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">Peace</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>

                                                    <span className="tag-list__separator"></span>

                                                    <span className="tag-label tag-label--operator tag-label--alert">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">not</span>
                                                        </span>
                                                    </span>
                                                    <span className="tag-label tag-label--alert">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">Trufeau</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--alert">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text">Bomb</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>

                                                    <span className="tag-list__separator tag-list__separator--blanc"></span>
                                                    <button className='nh-button nh-button--tertiary nh-button--small'>Clear</button>
                                                </div>
                                            </li>
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Fields searched</span>
                                                <div className="toggle-button__group toggle-button__group--spaced toggle-button__group--loose">
                                                        <button className="toggle-button toggle-button--no-txt-transform toggle-button--small toggle-button--active">Headline</button>
                                                        <button className="toggle-button toggle-button--no-txt-transform toggle-button--small toggle-button--active">Slugline</button>
                                                        <button className="toggle-button toggle-button--no-txt-transform toggle-button--small">Body</button>
                                                    </div>
                                            </li>
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Filters applied</span>
                                                <div className="tags-list">
                                                    <span className="tag-label">
                                                        <span className="tag-label--text-wrapper">
                                                        <span className="tag-label--text-label">Source:</span>
                                                            <span className="tag-label--text">Cision</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label">
                                                        <span className="tag-label--text-wrapper">
                                                        <span className="tag-label--text-label">Category:</span>
                                                            <span className="tag-label--text">Politics</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label">
                                                        <span className="tag-label--text-wrapper">
                                                        <span className="tag-label--text-label">From:</span>
                                                            <span className="tag-label--text">Feb 1st,2023</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label">
                                                        <span className="tag-label--text-wrapper">
                                                        <span className="tag-label--text-label">To:</span>
                                                            <span className="tag-label--text">Mar 1st,2023</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label">
                                                        <span className="tag-label--text-wrapper">
                                                        <span className="tag-label--text-label">Subject:</span>
                                                            <span className="tag-label--text">Affairs</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label">
                                                        <span className="tag-label--text-wrapper">
                                                        <span className="tag-label--text-label">Ranking:</span>
                                                            <span className="tag-label--text">2</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label">
                                                        <span className="tag-label--text-wrapper">
                                                        <span className="tag-label--text-label">Version:</span>
                                                            <span className="tag-label--text">2</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>

                                                    <span className="tag-list__separator tag-list__separator--blanc"></span>
                                                    <button className='nh-button nh-button--tertiary nh-button--small'>Clear filters</button>
                                                </div>
                                            </li>
                                            <li className="search-result__tags-list-row">
                                            </li>
                                            <li className="search-result__tags-list-row">
                                                <h4 className="pt-2">FOR TESTING ONLY:</h4>
                                            </li>

                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Test svih opcija</span>
                                                <div className="tags-list">
                                                    <span className="tag-label">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Default</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--darker">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Darker</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--inverse">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Inverse</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--highlight">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Highlight</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--success">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Success</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--warning">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Warning</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--alert">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Alert</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--info">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Info</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--highlight1">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Highlight 1</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span className="tag-label tag-label--highlight2">
                                                        <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Type:</span>
                                                            <span className="tag-label--text">Highlight 2</span>
                                                        </span>
                                                        <button className="tag-label__remove">
                                                            <i className="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                </div>
                                            </li>
                                            <li className="search-result__tags-list-row">
                                            <span className="search-result__tags-list-row-label">Icon Buttons</span>
                                                <button type="button" className="icon-button icon-button--primary" title=""><i className="icon--text"></i></button>
                                                <button type="button" className="icon-button icon-button--secondary" title=""><i className="icon--text"></i></button>
                                                <button type="button" className="icon-button" title=""><i className="icon--text"></i></button>

                                                <button type="button" className="icon-button icon-button--tertiary" title=""><i className="icon--text"></i></button>
                                                

                                                <button type="button" className="icon-button icon-button--primary icon-button--bordered" title=""><i className="icon--text"></i></button>
                                                <button type="button" className="icon-button icon-button--secondary icon-button--bordered" title=""><i className="icon--text"></i></button>
                                                <button type="button" className="icon-button icon-button--bordered" title=""><i className="icon--text"></i></button>

                                                <button type="button" className="icon-button icon-button--tertiary icon-button--bordered" title=""><i className="icon--text"></i></button>
                                                


                                            </li>
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Buttons</span>

                                                <button type="button" className="nh-button nh-button--primary" title=""><i className="icon--text"></i>Primary</button>
                                                <button type="button" className="nh-button nh-button--primary" title="">Primary</button>
                                                <button type="button" className="nh-button nh-button--secondary" title=""><i className="icon--text"></i>Secondary</button>
                                                <button type="button" className="nh-button nh-button--secondary" title="">Secondary</button>
                                                <button type="button" className="nh-button nh-button--tertiary" title=""><i className="icon--text"></i>Tertiary</button>
                                                <button type="button" className="nh-button nh-button--tertiary" title="">Tertiary</button>
                                            </li>
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Buttons -- small</span>

                                                <button type="button" className="nh-button nh-button--primary nh-button--small" title=""><i className="icon--text"></i>Primary</button>
                                                <button type="button" className="nh-button nh-button--primary nh-button--small" title="">Primary</button>
                                                <button type="button" className="nh-button nh-button--secondary nh-button--small" title=""><i className="icon--text"></i>Secondary</button>
                                                <button type="button" className="nh-button nh-button--secondary nh-button--small" title="">Secondary</button>
                                                <button type="button" className="nh-button nh-button--tertiary nh-button--small" title=""><i className="icon--text"></i>Tertiary</button>
                                                <button type="button" className="nh-button nh-button--tertiary nh-button--small" title="">Tertiary</button>
                                            </li>
                                        </ul>
                                    </div>
                                }
                                <div className="navbar navbar--flex navbar--small">
                                    <div className="navbar__inner navbar__inner--end">
                                        <div className="react-toggle__wrapper">
                                            <label for="all-versions" className="me-2">All Versions</label>
                                            <Toggle
                                                id="all-versions"
                                                defaultChecked={true}
                                                className='toggle-background'
                                                icons={false}
                                            />
                                        </div>
                                        <span className="navbar__divider"></span>
                                        <a href=" " className="icon-link--plain">
                                            <span className="icon-link__text">Change view</span>
                                            <i className="icon--list-view"></i>
                                        </a>
                                    </div>
                                </div>
                            </div>
                            <div className="wire-articles wire-articles--list">
                                <article className="wire-articles__item-wrap col-12 wire-item"><div className="wire-articles__item wire-articles__item--list" tabIndex="0"><div className="wire-articles__item-text-block"><h4 className="wire-articles__item-headline"><div className="no-bindable-select wire-articles__item-select"><label className="circle-checkbox"><input type="checkbox" className="css-checkbox" /><i></i></label></div><div className="wire-articles__item-headline-inner">Correct me later on and see what fields appear</div></h4><div className="wire-articles__item__meta"><div className="wire-articles__item__icons"><span className="wire-articles__item__icon"><i className="icon--text icon--gray-dark"></i></span></div><div className="wire-articles__item__meta-info"><span className="bold">Correctme</span><span><span></span><span><span>The Canadian Press</span></span><span><span> // </span></span><span><span>1 words</span></span><span><span> // </span></span><span><time dateTime="12:51 19/12/2022">12:51 19/12/2022</time></span></span></div></div><div className="wire-articles__item__text"><p>hello3</p></div></div><div className="wire-articles__item-actions"><div className="btn-group"><button className="icon-button" aria-label="More Actions"><i className="icon--more icon--gray-dark"></i></button></div><button type="button" className="icon-button icon-button--primary" title="" aria-label="Share" data-original-title="Share"><i className="icon--share"></i></button><button type="button" className="icon-button icon-button--primary" title="" aria-label="Save" data-original-title="Save"><i className="icon--bookmark-add"></i></button></div></div></article>
                                <article className="wire-articles__item-wrap col-12 wire-item"><div className="wire-articles__item wire-articles__item--list" tabIndex="0"><div className="wire-articles__item-text-block"><h4 className="wire-articles__item-headline"><div className="no-bindable-select wire-articles__item-select"><label className="circle-checkbox"><input type="checkbox" className="css-checkbox" /><i></i></label></div><div className="wire-articles__item-headline-inner">Correct me later on and see what fields appear</div></h4><div className="wire-articles__item__meta"><div className="wire-articles__item__icons"><span className="wire-articles__item__icon"><i className="icon--text icon--gray-dark"></i></span></div><div className="wire-articles__item__meta-info"><span className="bold">Correctme</span><span><span></span><span><span>The Canadian Press</span></span><span><span> // </span></span><span><span>1 words</span></span><span><span> // </span></span><span><time dateTime="12:51 19/12/2022">12:51 19/12/2022</time></span></span></div></div><div className="wire-articles__item__text"><p>hello3</p></div></div><div className="wire-articles__item-actions"><div className="btn-group"><button className="icon-button" aria-label="More Actions"><i className="icon--more icon--gray-dark"></i></button></div><button type="button" className="icon-button icon-button--primary" title="" aria-label="Share" data-original-title="Share"><i className="icon--share"></i></button><button type="button" className="icon-button icon-button--primary" title="" aria-label="Save" data-original-title="Save"><i className="icon--bookmark-add"></i></button></div></div></article>
                                {/* AGENDA Item for testing */}
                                <article className="wire-articles__item-wrap col-12 agenda-item">
                                    <div className="wire-articles__item wire-articles__item--list wire-articles__item--not-covering" tabindex="0">
                                        <div className="wire-articles__item-text-block">
                                            <h4 className="wire-articles__item-headline">
                                                <div className="no-bindable-select wire-articles__item-select">
                                                    <label className="circle-checkbox">
                                                        <input type="checkbox" className="css-checkbox" /><i></i>
                                                    </label>
                                                </div>
                                                <div className="wire-articles__item-headline-inner">Agenda item for testing, isco spice up last day of transfers in Germany</div>
                                            </h4>
                                            <div className="wire-articles__item__meta wire-articles__item__meta--">
                                                <div className="wire-articles__item__icons wire-articles__item__icons--dashed-border">
                                                    <span className="wire-articles__item__icon"><i className="icon--calendar"></i></span>
                                                </div>
                                                <div className="wire-articles__item__meta-time wire-articles__item__meta-time--border-right">
                                                    <span>20/06/2023 to 23/06/2023</span>
                                                </div>
                                                <div className="wire-articles__item__icons wire-articles__item__icons--dashed-border">
                                                    <span className="wire-articles__item__icon coverage--completed" title=" Text coverage MEL-TEST-NBA-RAPTORS available (updated)"><i className="icon--coverage-text"></i></span>
                                                    <span className="wire-articles__item__icon coverage--assigned" title=" Planned Picture coverage MEL-TEST-NBA-RAPTORS, expected Apr 13th, 2023 at 23:00"><i className="icon--coverage-photo"></i></span>
                                                    <span className="wire-articles__item__icon coverage--assigned" title=" Planned Text coverage MEL-TEST-NBA-RAPTORS-sidebar, expected Apr 13th, 2023 at 23:00"><i className="icon--coverage-text"></i></span>
                                                    <span className="wire-articles__item__icon coverage--completed" title=" Text coverage MEL-TEST-April13-Breaking available (update to come)"><i className="icon--coverage-text"><i className="blue-circle"></i></i></span>
                                                </div>
                                                <div className="wire-articles__item__meta-info align-items-center">
                                                    <span><i className="icon-small--location icon--gray-dark"></i></span>
                                                    <span className="me-2 align-self-stretch">Messezentrum Salzburg GmbH, Am Messezentrum 1, Salzburg, Austria</span>
                                                </div>
                                            </div>
                                            <div className="wire-articles__item__text">
                                                <p>DÜSSELDORF, Germany (AP) — Portugal left back João Cancelo’s switch to Bayern Munich and former Real Madrid star Isco Alarcón's potential signing by Union Berlin brought excitement to the last day of the winter transfer period in Germany. After seeing...</p>
                                            </div>
                                        </div>
                                        <div className="wire-articles__item-actions">
                                            <div className="btn-group">
                                                <button className="icon-button icon-button--secondary" aria-label="More Actions"><i className="icon--more"></i></button>
                                            </div>
                                            <button type="button" className="icon-button icon-button--primary" title="" aria-label="Share" data-bs-original-title="Share"><i className="icon--share"></i></button>
                                            <button type="button" className="icon-button icon-button--primary" title="" aria-label="Save" data-bs-original-title="Save"><i className="icon--bookmark-add"></i></button>
                                        </div>
                                    </div>
                                </article>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
            {isAdvancedSearchShown && <AdvancedSearch />}
            {isAdvancedSearchTipsShown && <AdvancedSearchTips />}
        </div>
    );
  }
  
  export default Wire;
  