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
                                        <img src='static/search_clear.png' width='16' height='16'/>
                                    </button>
                                    <button className='btn btn-outline-secondary' type='submit'>
                                        Search
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div className="content-bar__right">
                        <div className="d-flex align-items-center px-2 px-sm-3">
                            <div className="d-flex align-items-center">
                                <label htmlFor="all-versions" className="mr-2">All Versions</label>
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
                    <article className="wire-articles__item-wrap col-12 wire-item"><div className="wire-articles__item wire-articles__item--list" tabIndex="0"><div className="wire-articles__item-text"><h4 className="wire-articles__item-headline"><div className="no-bindable-select wire-articles__item-select"><label className="circle-checkbox"><input type="checkbox" className="css-checkbox" /><i></i></label></div><div className="wire-articles__item-headline-inner">Correct me later on and see what fields appear</div></h4><div className="wire-articles__item__meta"><div className="wire-articles__item__icons"><span className="wire-articles__item__icon"><i className="icon--text icon--gray-dark"></i></span></div><div className="wire-articles__item__meta-info"><span className="bold">Correctme</span><span><span></span><span><span>The Canadian Press</span></span><span><span> // </span></span><span><span>1 words</span></span><span><span> // </span></span><span><time dateTime="12:51 19/12/2022">12:51 19/12/2022</time></span></span></div></div><div className="wire-articles__item__text"><p>hello3</p></div></div><div className="wire-articles__item-actions"><div className="btn-group"><button className="icon-button" aria-label="More Actions"><i className="icon--more icon--gray-dark"></i></button></div><button type="button" className="icon-button" title="" aria-label="Share" data-original-title="Share"><i className="icon--share"></i></button><button type="button" className="icon-button" title="" aria-label="Save" data-original-title="Save"><i className="icon--bookmark-add"></i></button></div></div></article>
                    </div>
                </div>
                </div>
            </section>
        </div>
    );
  }

  export default WireOld;
