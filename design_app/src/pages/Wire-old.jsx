import React from 'react';
import Toggle from 'react-toggle';
import classNames from 'classnames';
import 'react-toggle/style.css';
//import { useNavigate } from 'react-router-dom';

function WireOld() {
    return (
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
                                    <i class="icon--search"></i>
                                </button>
                            </div>
                        </form>
                    </div>

                    <div className="content-bar__right">
                        <div className="d-flex align-items-center px-2 px-sm-3">
                            <div className="d-flex align-items-center">
                                <label htmlFor="all-versions" className="me-2 mb-0">All Versions</label>
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
                    </div>
                </nav>
            </section>
            <section className="content-main">
                <div className="wire-column--3">
                <div className="wire-column__main">
                    <div className="wire-articles wire-articles--list">
                    <article className="wire-articles__item-wrap col-12 wire-item"><div className="wire-articles__item wire-articles__item--list" tabIndex="0"><div className="wire-articles__item-text-block"><h4 className="wire-articles__item-headline"><div className="no-bindable-select wire-articles__item-select"><label className="circle-checkbox"><input type="checkbox" className="css-checkbox" /><i></i></label></div><div className="wire-articles__item-headline-inner">Correct me later on and see what fields appear</div></h4><div className="wire-articles__item__meta"><div className="wire-articles__item__icons"><span className="wire-articles__item__icon"><i className="icon--text icon--gray-dark"></i></span></div><div className="wire-articles__item__meta-info"><span className="bold">Correctme</span><span><span></span><span><span>The Canadian Press</span></span><span><span> // </span></span><span><span>1 words</span></span><span><span> // </span></span><span><time dateTime="12:51 19/12/2022">12:51 19/12/2022</time></span></span></div></div><div className="wire-articles__item__text"><p>hello3</p></div></div><div className="wire-articles__item-actions"><div className="btn-group"><button className="icon-button" aria-label="More Actions"><i className="icon--more icon--gray-dark"></i></button></div><button type="button" className="icon-button" title="" aria-label="Share" data-original-title="Share"><i className="icon--share"></i></button><button type="button" className="icon-button" title="" aria-label="Save" data-original-title="Save"><i className="icon--bookmark-add"></i></button></div></div></article>
                    </div>
                </div>
                </div>
            </section>
        </div>
    );
  }

  export default WireOld;
