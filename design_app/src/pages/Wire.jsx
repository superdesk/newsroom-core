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


    return (
        <div className="wire-wrap">
            <div className="content">
                <section className="content-header">
                    <h3 className="a11y-only">Wire Content</h3>
                    <nav className="content-bar navbar justify-content-start flex-nowrap flex-sm-wrap">
                        <button className="content-bar__menu content-bar__menu--nav" title="" aria-label="Open filter panel" data-original-title="Open filter panel"><i className="icon--hamburger"></i></button>
            
                        <div className="search d-flex align-items-center">
                            <span className="search__icon">
                                <i className="icon--search icon--gray" />
                            </span>
                            <div className='search__form input-group'>
                                <form className='d-flex align-items-center' role="search" aria-label='search'>
                                    <input
                                        type='text'
                                        name='q'
                                        className='search__input form-control'
                                        placeholder='Search for...'
                                        aria-label='Search for...'
                                    />
                                    <div className='search__form__buttons'>
                                        <button
                                            className='btn search__clear'
                                            aria-label='Search clear'
                                            type="reset"
                                        >
                                            <img src='src/assets/images/search_clear.png' width='16' height='16'/>
                                        </button>
                                        <button className="btn btn-outline-secondary" type='submit'>
                                            Search
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                        <div className="mx-2 d-flex gap-2">
                            <button onClick={handleClickAdvancedSearch} className='btn btn-primary' >Advanced Search</button>
                            <button onClick={handleClickAdvancedSearchTips} className="icon-button icon-button--bordered" aria-label="Info"><i className="icon--info"></i></button>
                        </div>
                        {/* <div className="content-bar__right">
                            <div className="d-flex align-items-center px-2 px-sm-3">
                                <div className="d-flex align-items-center">
                                    <label for="all-versions" className="mr-2">All Versions</label>
                                    <Toggle
                                        id="all-versions"
                                        defaultChecked={true}
                                        className='toggle-background'
                                        icons={false}
                                    />
                                </div>
                            </div>
                            <div className="btn-group list-view__options" data-original-title="" title="">
                                <button className="content-bar__menu" title="Change view" aria-label="Change view" role="button"><i className="icon--list-view"></i>
                                </button>
                            </div>
                        </div>                         */}
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
                                    <div className="collapsible-box collapsible-box--open">
                                        <div className="collapsible-box__header" onClick={colorHandler}>
                                            <h4 className="collapsible-box__header-title">Politics ATP World Tour Millennium Estoril Open Results</h4>
                                            <div className="collapsible-box__header-caret">
                                                <i class="icon--arrow-right icon--collapsible-open"></i>
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
                                                    <a className="topic-list__item-link" aria-selected="false" href="">
                                                        <span className="topic-list__item-link_label">Donetsk</span>
                                                        <span className="badge rounded-pill bg-info">8</span>
                                                    </a>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>

                                    <div className="collapsible-box">
                                        <div className="collapsible-box__header 11" onClick={colorHandler}>
                                            <h4 className="collapsible-box__header-title">Culture</h4>
                                            <div className="collapsible-box__header-caret">
                                                <i class="icon--arrow-right icon--collapsible-closed"></i>
                                            </div>
                                        </div>
                                        <div className="collapsible-box__content">
                                        
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
                    </div>
                        <div className="wire-column__main">
                            <div className="wire-column__main-header-container">
                                <div className="navbar navbar--flex line-shadow-end--light">
                                    <div className="search-result-count">12,339 results</div>
                                    <div className="navbar__button-group">
                                        <button class="btn btn-outline-secondary">Clear all</button>
                                        <button onClick={handleClickTag} class="icon-button icon-button--bordered">
                                            {isTagSectionShown && <i class="icon--arrow-right icon--collapsible-open"></i>}
                                            {!isTagSectionShown && <i class="icon--arrow-right icon--collapsible-closed"></i>}
                                        </button>
                                    </div>
                                </div>
                                {isTagSectionShown &&
                                    <div className="navbar navbar--flex line-shadow-end--light navbar--auto-height">
                                        <ul className="search-result__tags-list">
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Topic</span>
                                                <div className="tags-list">
                                                    <span class="tag-label tag-label--inverse">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">My Ukraine War Topic</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                </div>
                                                <div class="tags-list-row__button-group">
                                                    <button class="btn btn-outline-secondary btn-responsive btn--small">Update topic</button>
                                                    <button class="btn btn-outline-secondary btn-responsive btn--small">Save as new topic</button>
                                                </div>
                                            </li>
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Text fields</span>
                                                <div className="tags-list">
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">Headline</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">Headline</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                </div>
                                            </li>
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Search terms</span>
                                                <div className="tags-list">
                                                    <span class="tag-label tag-label--info">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">Zelensky</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--operator tag-label--info">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">or</span>
                                                        </span>
                                                    </span>
                                                    <span class="tag-label tag-label--info">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">Peace</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--operator">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">and</span>
                                                        </span>
                                                    </span>
                                                    <span class="tag-label tag-label--success">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">Russia</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--operator tag-label--success">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">and</span>
                                                        </span>
                                                    </span>
                                                    <span class="tag-label tag-label--success">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">War</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--operator">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">and</span>
                                                        </span>
                                                    </span>
                                                    <span class="tag-label tag-label--operator tag-label--alert">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">not</span>
                                                        </span>
                                                    </span>
                                                    <span class="tag-label tag-label--alert">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">Trufeau</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--operator tag-label--alert">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">not</span>
                                                        </span>
                                                    </span>
                                                    <span class="tag-label tag-label--alert">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text">Bomb</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                </div>
                                            </li>
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Filters applied</span>
                                                <div className="tags-list">
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                        <span class="tag-label--text-label">Source:</span>
                                                            <span class="tag-label--text">Cision</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                        <span class="tag-label--text-label">Category:</span>
                                                            <span class="tag-label--text">Politics</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                        <span class="tag-label--text-label">From:</span>
                                                            <span class="tag-label--text">Feb 1st,2023</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                        <span class="tag-label--text-label">To:</span>
                                                            <span class="tag-label--text">Mar 1st,2023</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                        <span class="tag-label--text-label">Subject:</span>
                                                            <span class="tag-label--text">Affairs</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                        <span class="tag-label--text-label">Ranking:</span>
                                                            <span class="tag-label--text">2</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                        <span class="tag-label--text-label">Version:</span>
                                                            <span class="tag-label--text">2</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                </div>
                                            </li>
                                            <li className="search-result__tags-list-row">
                                                <span className="search-result__tags-list-row-label">Test svih opcija</span>
                                                <div className="tags-list">
                                                    <span class="tag-label">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Default</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--darker">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Darker</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--inverse">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Inverse</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--highlight">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Highlight</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--success">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Success</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--warning">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Warning</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--alert">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Alert</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--info">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Info</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--highlight1">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Highlight 1</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                    <span class="tag-label tag-label--highlight2">
                                                        <span class="tag-label--text-wrapper">
                                                            <span class="tag-label--text-label">Type:</span>
                                                            <span class="tag-label--text">Highlight 2</span>
                                                        </span>
                                                        <button class="tag-label__remove">
                                                            <i class="icon--close-thin"></i>
                                                        </button>
                                                    </span>
                                                </div>
                                            </li>
                                        </ul>
                                    </div>
                                }
                                <div className="navbar navbar--flex navbar--small">
                                    <div className="navbar__inner navbar__inner--end">
                                        <div className="react-toggle__wrapper">
                                            <label for="all-versions" className="mr-2">All Versions</label>
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
                                            <i class="icon--list-view"></i>
                                        </a>
                                    </div>
                                </div>
                            </div>
                            <div className="wire-articles wire-articles--list">
                                <article className="wire-articles__item-wrap col-12 wire-item"><div className="wire-articles__item wire-articles__item--list" tabIndex="0"><div className="wire-articles__item-text"><h4 className="wire-articles__item-headline"><div className="no-bindable-select wire-articles__item-select"><label className="circle-checkbox"><input type="checkbox" className="css-checkbox" /><i></i></label></div><div className="wire-articles__item-headline-inner">Correct me later on and see what fields appear</div></h4><div className="wire-articles__item__meta"><div className="wire-articles__item__icons"><span className="wire-articles__item__icon"><i className="icon--text icon--gray-dark"></i></span></div><div className="wire-articles__item__meta-info"><span className="bold">Correctme</span><span><span></span><span><span>The Canadian Press</span></span><span><span> // </span></span><span><span>1 words</span></span><span><span> // </span></span><span><time dateTime="12:51 19/12/2022">12:51 19/12/2022</time></span></span></div></div><div className="wire-articles__item__text"><p>hello3</p></div></div><div className="wire-articles__item-actions"><div className="btn-group"><button className="icon-button" aria-label="More Actions"><i className="icon--more icon--gray-dark"></i></button></div><button type="button" className="icon-button" title="" aria-label="Share" data-original-title="Share"><i className="icon--share"></i></button><button type="button" className="icon-button" title="" aria-label="Save" data-original-title="Save"><i className="icon--bookmark-add"></i></button></div></div></article>
                                <article className="wire-articles__item-wrap col-12 wire-item"><div className="wire-articles__item wire-articles__item--list" tabIndex="0"><div className="wire-articles__item-text"><h4 className="wire-articles__item-headline"><div className="no-bindable-select wire-articles__item-select"><label className="circle-checkbox"><input type="checkbox" className="css-checkbox" /><i></i></label></div><div className="wire-articles__item-headline-inner">Correct me later on and see what fields appear</div></h4><div className="wire-articles__item__meta"><div className="wire-articles__item__icons"><span className="wire-articles__item__icon"><i className="icon--text icon--gray-dark"></i></span></div><div className="wire-articles__item__meta-info"><span className="bold">Correctme</span><span><span></span><span><span>The Canadian Press</span></span><span><span> // </span></span><span><span>1 words</span></span><span><span> // </span></span><span><time dateTime="12:51 19/12/2022">12:51 19/12/2022</time></span></span></div></div><div className="wire-articles__item__text"><p>hello3</p></div></div><div className="wire-articles__item-actions"><div className="btn-group"><button className="icon-button" aria-label="More Actions"><i className="icon--more icon--gray-dark"></i></button></div><button type="button" className="icon-button" title="" aria-label="Share" data-original-title="Share"><i className="icon--share"></i></button><button type="button" className="icon-button" title="" aria-label="Save" data-original-title="Save"><i className="icon--bookmark-add"></i></button></div></div></article>
                                <article className="wire-articles__item-wrap col-12 wire-item"><div className="wire-articles__item wire-articles__item--list" tabIndex="0"><div className="wire-articles__item-text"><h4 className="wire-articles__item-headline"><div className="no-bindable-select wire-articles__item-select"><label className="circle-checkbox"><input type="checkbox" className="css-checkbox" /><i></i></label></div><div className="wire-articles__item-headline-inner">Correct me later on and see what fields appear</div></h4><div className="wire-articles__item__meta"><div className="wire-articles__item__icons"><span className="wire-articles__item__icon"><i className="icon--text icon--gray-dark"></i></span></div><div className="wire-articles__item__meta-info"><span className="bold">Correctme</span><span><span></span><span><span>The Canadian Press</span></span><span><span> // </span></span><span><span>1 words</span></span><span><span> // </span></span><span><time dateTime="12:51 19/12/2022">12:51 19/12/2022</time></span></span></div></div><div className="wire-articles__item__text"><p>hello3</p></div></div><div className="wire-articles__item-actions"><div className="btn-group"><button className="icon-button" aria-label="More Actions"><i className="icon--more icon--gray-dark"></i></button></div><button type="button" className="icon-button" title="" aria-label="Share" data-original-title="Share"><i className="icon--share"></i></button><button type="button" className="icon-button" title="" aria-label="Save" data-original-title="Save"><i className="icon--bookmark-add"></i></button></div></div></article>
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
  