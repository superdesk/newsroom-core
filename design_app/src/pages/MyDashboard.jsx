import React from 'react';

function MyDashboard() {
    return (
        <div className="full-page-layout__wrapper" role='dialog' aria-label="My Dashboard">
            <div className="full-page-layout">
                <div className="full-page-layout__header">
                    <h5 className="full-page-layout__header-title">Personalize Home</h5>
                    <button className="profile__profile-content-close" aria-label='Close' role="button">
                        <i className="icon--close-thin" />
                    </button>
                </div>
                <div className="full-page-layout__content">
                    <aside className="full-page-layout__content-aside">
                        <div className="full-page-layout__content-aside-inner">
                            <p className='font-size--medium text-color--muted mt-1 mb-3'>Select up to 6 Topics you want to display on your personal Home screen.</p>
                            <p className='font-size--large'>4 of 6 topics selected</p>
                            <div className="d-flex justify-content-between pb-3">
                                <div className="toggle-button__group toggle-button__group--stretch-items w-100 mx-auto">
                                    <button className="toggle-button toggle-button--active">My Topics</button>
                                    <button className="toggle-button">Company Topics</button>
                                </div>
                            </div>
                            <div class="search search--small search--with-icon search--bordered m-0">
                                <form class="search__form" role="search" aria-label="search">
                                    <i class="icon--search icon--muted-2"></i>
                                    <input type="text" name="q" class="search__input form-control" placeholder="Search Topics" aria-label="Search Topics" />
                                    <div class="search__form-buttons">
                                        <button class="search__button-clear" aria-label="Clear search" type="reset">
                                            <svg fill="none" height="18" viewBox="0 0 18 18" width="18" xmlns="http://www.w3.org/2000/svg">
                                                <path clip-rule="evenodd" d="m9 18c4.9706 0 9-4.0294 9-9 0-4.97056-4.0294-9-9-9-4.97056 0-9 4.02944-9 9 0 4.9706 4.02944 9 9 9zm4.9884-12.58679-3.571 3.57514 3.5826 3.58675-1.4126 1.4143-3.58252-3.5868-3.59233 3.5965-1.41255-1.4142 3.59234-3.59655-3.54174-3.54592 1.41254-1.41422 3.54174 3.54593 3.57092-3.57515z" fill="var(--color-text)" fill-rule="evenodd" opacity="1"></path>
                                            </svg>
                                        </button>
                                    </div>
                                </form>
                            </div>

                            {/* // EMPTY STATE -- enable if there ar no Saved Topics (e.g. My Wire Topics or My Agenda Topics) */}
                            {/* <div className="empty-state__container mt-3">
                                <div className="empty-state">
                                    <figure className="empty-state__graphic">
                                        <img src="/static/empty-states/empty_state--small.svg" role="presentation" alt="" />
                                    </figure>
                                    <figcaption className="empty-state__text">
                                        <h4 className="empty-state__text-heading">You don't have any saved Topics yet</h4>
                                        <p className="empty-state__text-description">
                                            You can create Topics by saving search terms and/or filters from the Wire and Agenda sections.
                                        </p>
                                        <div className="empty-state__links">
                                            <a className="" href="">Go to Wire</a>
                                            <a className="" href="">Go to Agenda</a>
                                        </div>
                                    </figcaption>
                                </div>
                            </div> */}

                            <div className='boxed-checklist'>
                                <div className="form-check form-check--checked">
                                    <input type="checkbox" className="form-check-input" checked id="pr1" tabIndex="0"></input>
                                    <label className="form-check-label" htmlFor="pr1">My Ukraine War Topic</label>
                                </div>

                                <div className="form-check form-check--checked">
                                    <input type="checkbox" className="form-check-input" checked id="pr2" tabIndex="0"></input>
                                    <label className="form-check-label" htmlFor="pr2">Turkey-Syria earthquake</label>
                                </div>

                                <div className="form-check">
                                    <input type="checkbox" className="form-check-input" id="pr3" tabIndex="0"></input>
                                    <label className="form-check-label" htmlFor="pr3">My Topic One</label>
                                </div>

                                <div className="form-check">
                                    <input type="checkbox" className="form-check-input" id="pr4" tabIndex="0"></input>
                                    <label className="form-check-label" htmlFor="pr4">My Topic Two</label>
                                </div>

                                <div className="form-check">
                                    <input type="checkbox" className="form-check-input" id="pr5" tabIndex="0"></input>
                                    <label className="form-check-label" htmlFor="pr5">My Topic Three</label>
                                </div>
                            </div>
                        </div>
                    </aside>

                    <div className="full-page-layout__content-main">

                        <input  placeholder="Personal home name" type="text" className="form-control" value="My Dashboard" />

                        {/* // EMPTY STATE -- enable if there ar no Topics added to the personal dashboare */}

                        {/* <div className="empty-state__container empty-state__container--full-height">
                            <div className="empty-state empty-state--large">
                                <figure className="empty-state__graphic">
                                    <img src="/static/empty-states/empty_state--large.svg" role="presentation" alt="" />
                                </figure>
                                <figcaption className="empty-state__text">
                                    <h4 className="empty-state__text-heading">You don't have any saved Topics yet</h4>
                                    <p className="empty-state__text-description">
                                        You can create Topics by saving search terms and/or filters from the Wire and Agenda sections.
                                    </p>
                                </figcaption>
                            </div>
                        </div> */}

                        <div className="py-3 mt-4 mb-2 border border--medium border-start-0 border-end-0 border--dotted">
                            <p className='font-size--medium text-color--muted m-0'><span className='text-color--default fw-bold'>Hint:</span> Drag and drop items to change the order. This will change the order of the topics are displayed on the Home screen.</p>
                        </div>

                        <div className="simple-card__list pt-3">

                            <div className="simple-card flex-row simple-card--compact simple-card--draggable">
                                <div className='simple-card__content'>
                                    <h6 className="simple-card__headline" title="">My Ukraine War Topic</h6>
                                    <div className="simple-card__row">
                                        <div className="simple-card__column simple-card__column--align-start">
                                            <span className="simple-card__date">My Topics</span>
                                        </div>
                                    </div>
                                </div>
                                <div className='simple-card__actions'>
                                    <button type="button" className="icon-button icon-button--secondary icon-button--small" title="" aria-label="Delete"><i className="icon--trash"></i></button>
                                </div>
                            </div>

                            <div className="simple-card flex-row simple-card--compact simple-card--draggable">
                                <div className='simple-card__content'>
                                    <h6 className="simple-card__headline" title="">Turkey-Syria earthquake</h6>
                                    <div className="simple-card__row">
                                        <div className="simple-card__column simple-card__column--align-start">
                                            <span className="simple-card__date">My Topics</span>
                                        </div>
                                    </div>
                                </div>
                                <div className='simple-card__actions'>
                                    <button type="button" className="icon-button icon-button--secondary icon-button--small" title="" aria-label="Delete"><i className="icon--trash"></i></button>
                                </div>
                            </div>

                            <div className="simple-card flex-row simple-card--compact simple-card--draggable">
                                <div className='simple-card__content'>
                                    <h6 className="simple-card__headline" title="">Politics</h6>
                                    <div className="simple-card__row">
                                        <div className="simple-card__column simple-card__column--align-start">
                                            <span className="simple-card__date">Company Topics</span>
                                        </div>
                                    </div>
                                </div>
                                <div className='simple-card__actions'>
                                    <button type="button" className="icon-button icon-button--secondary icon-button--small" title="" aria-label="Delete"><i className="icon--trash"></i></button>
                                </div>
                            </div>

                            <div className="simple-card flex-row simple-card--compact simple-card--draggable">
                                <div className='simple-card__content'>
                                    <h6 className="simple-card__headline" title="">Ecology</h6>
                                    <div className="simple-card__row">
                                        <div className="simple-card__column simple-card__column--align-start">
                                            <span className="simple-card__date">Company Topics</span>
                                        </div>
                                    </div>
                                </div>
                                <div className='simple-card__actions'>
                                    <button type="button" className="icon-button icon-button--secondary icon-button--small" title="" aria-label="Delete"><i className="icon--trash"></i></button>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
                <div className='full-page-layout__footer'>
                    <input type="button" className="nh-button nh-button--secondary" value="Cancel" />
                    <input type="button" className="nh-button nh-button--primary" value="Save" />
                </div>
            </div>

        </div>
    );
  }
  
  export default MyDashboard;