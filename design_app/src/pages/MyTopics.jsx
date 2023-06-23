import React from 'react';
import EditTopic from '../components/EditTopic';

function MyTopics() {
    return (
        <div id="user-profile-app" className="settingsWrap">
            <div className="profile-container" role='dialog' aria-label="My Topics">
                <div className="profileWrap">
                    <div className="profile__mobile-close d-md-none">
                        <button className="icon-button" aria-label='Close' onClick={'/wire'}>
                            <i className="icon--close-thin icon--gray-dark" />
                        </button>
                    </div>
                    <nav className='profile__side-navigation' id='profile-menu'>
                        <div className="profile__group">
                            <figure className="profile__avatar initials">
                                <span className="profile__characters">JL</span>
                            </figure>
                            <div className="profile__name-container">
                                <h5 className="profile__name">Jeffrey Lebowski</h5>
                            </div>
                        </div>
                        <div className="profile__side-navigation__items">
                            <a href="#" className="nh-button btn w-100 nh-button--secondary" name="profile">My Profile</a>
                            <a href="#" className="nh-button btn w-100 nh-button--primary" name="topics">My Wire Topics</a>
                            <a href="#" className="nh-button btn w-100 nh-button--secondary" name="events">My Agenda Topics</a>
                        </div>
                    </nav>
                    <div className="profile__profile-content">
                        <section className="profile__profile-content-header">
                            <h5 className="ps-xl-4 mb-0">
                                My Topics
                            </h5>
                            <button className="profile__profile-content-close" aria-label='Close' role="button">
                                <i className="icon--close-thin" />
                            </button>
                        </section>
                        <section className="profile__profile-content-main">

                            <div className="profile-content profile-content--topics">
                                <div className="profile-content__main d-flex flex-column flex-grow-1">
                                    <div className="d-flex justify-content-between pt-xl-4 pt-3">
                                        <div className="toggle-button__group toggle-button__group--navbar ms-0 me-3">
                                            <button className="toggle-button toggle-button--active">My Topics</button>
                                            <button className="toggle-button">Company Topics</button>
                                        </div>
                                        <div className="toggle-button__group toggle-button__group--navbar ms-0 me-0">
                                            <button type="button" class="nh-button nh-button--tertiary" title=""><i class="icon--folder-create"></i>New folder</button>
                                        </div>
                                    </div>
                                    <div className="simple-card__list pt-xl-4 pt-3">
                                        <div className="simple-card__group">
                                            <div className="simple-card__group-header">
                                                <button type="button" class="icon-button icon-button--tertiary" title=""><i class="icon--minus"></i></button>
                                                <div className="simple-card__group-header-title">
                                                    <i class="icon--folder"></i>
                                                    <span className="simple-card__group-header-name">My New folder</span>
                                                </div>
                                                <span class="badge badge--neutral rounded-pill me-2">4</span>
                                                <div className="simple-card__group-header-actions">
                                                    <button type="button" class="icon-button icon-button--tertiary" title=""><i class="icon--more"></i></button>
                                                </div>
                                            </div>
                                            <div className="simple-card__group-content">
                                                <div className="simple-card simple-card--draggable">
                                                    <div className="simple-card__header simple-card__header-with-icons">
                                                        <h6 className="simple-card__headline" title="">My Topic 1</h6>
                                                        <div className="simple-card__icons">
                                                            <button type="button" className="icon-button icon-button--primary" title="" aria-label="Remove from folder"><i className="icon--folder-remove-from"></i></button>
                                                            <button type="button" className="icon-button icon-button--primary" title="" aria-label="Edit"><i className="icon--edit"></i></button>
                                                            <button type="button" className="icon-button icon-button--primary" title="" aria-label="Share"><i className="icon--share"></i></button>
                                                            <button type="button" className="icon-button icon-button--primary" title="" aria-label="Delete"><i className="icon--trash"></i></button>
                                                        </div>
                                                    </div>
                                                    <p className="simple-card__description">
                                                        Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum. Aenean lacinia bibendum nulla sed consectetur.
                                                    </p>
                                                    <div className="simple-card__row simple-card__row--space-between">
                                                        <div className="simple-card__column simple-card__column--align-start">
                                                            <span className="simple-card__date">Created on 29.05.2023 @ 12:38</span>
                                                            <span className="simple-card__date">Updated on 31.05.2023 @ 14:02</span>
                                                        </div>
                                                        <div className="simple-card__column simple-card__column--align-end">
                                                            <span className="simple-card__notification-info">
                                                                <i class="icon--alert"></i>
                                                                <span className="label--rounded label--alert">Scheduled</span>
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="simple-card simple-card--draggable simple-card--selected">
                                            <div className="simple-card__header simple-card__header-with-icons">
                                                    <h6 className="simple-card__headline" title="">My Ukraine War Topic</h6>
                                                <div className="simple-card__icons">
                                                    <button type="button" className="icon-button icon-button--primary" title="" aria-label="Remove from folder"><i className="icon--folder-add-to"></i></button>
                                                    <button type="button" className="icon-button icon-button--primary" title="" aria-label="Edit"><i className="icon--edit"></i></button>
                                                    <button type="button" className="icon-button icon-button--primary" title="" aria-label="Share"><i className="icon--share"></i></button>
                                                    <button type="button" className="icon-button icon-button--primary" title="" aria-label="Delete"><i className="icon--trash"></i></button>
                                                </div>
                                            </div>
                                            <p className="simple-card__description">
                                                Praesent commodo cursus magna, vel scelerisque nisl consectetur et. Nullam id dolor id nibh ultricies vehicula ut id elit.
                                            </p>
                                            <div className="simple-card__row simple-card__row--space-between">
                                                <div className="simple-card__column simple-card__column--align-start">
                                                    <span className="simple-card__date">Created on 25.05.2023 @ 14:02</span>
                                                    <span className="simple-card__date">Updated on 29.05.2023 @ 16:29</span>
                                                </div>
                                                <div className="simple-card__column simple-card__column--align-end">
                                                    <span className="simple-card__notification-info">
                                                        <i class="icon--alert"></i>
                                                        <span className="label--rounded label--alert">Real-Time</span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="simple-card simple-card--draggable">
                                            <div className="simple-card__header simple-card__header-with-icons">
                                                <h6 className="simple-card__headline" title="">My Topic 2</h6>
                                                <div className="simple-card__icons">
                                                    <button type="button" className="icon-button icon-button--primary" title="" aria-label="Remove from folder"><i className="icon--folder-add-to"></i></button>
                                                    <button type="button" className="icon-button icon-button--primary" title="" aria-label="Edit"><i className="icon--edit"></i></button>
                                                    <button type="button" className="icon-button icon-button--primary" title="" aria-label="Share"><i className="icon--share"></i></button>
                                                    <button type="button" className="icon-button icon-button--primary" title="" aria-label="Delete"><i className="icon--trash"></i></button>
                                                </div>
                                            </div>
                                            <p className="simple-card__description">
                                                Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum. Aenean lacinia bibendum nulla sed consectetur.
                                            </p>
                                            <div className="simple-card__row simple-card__row--space-between">
                                                <div className="simple-card__column simple-card__column--align-start">
                                                    <span className="simple-card__date">Created on 29.05.2023 @ 12:38</span>
                                                    <span className="simple-card__date">Updated on 31.05.2023 @ 14:02</span>
                                                </div>
                                                <div className="simple-card__column simple-card__column--align-end">
                                                    <span className="simple-card__notification-info">
                                                        <i class="icon--alert"></i>
                                                        <span className="label--rounded label--alert">Scheduled</span>
                                                    </span>
                                                </div>
                                            </div>
                                        </div>


                                        <h4 className="mb-0 mt-3 text-info">States and variations:</h4>

                                        <small className="text-info">Folder Creation (initiated from the 'NEW FOLDER' button at the top):</small>
                                        <div className="simple-card__group">
                                            <div className="simple-card__group-header simple-card__group-header--selected">
                                                <div className="d-flex flex-row flex-grow-1 align-items-center gap-2 ps-1">
                                                    <i class="icon--folder icon--small"></i>
                                                    <input type="text" aria-label="Folder name" className="form-control form-control--small" maxLength="30" value="My New folder" />
                                                    <button type="button" class="icon-button icon-button--secondary icon-button--bordered icon-button--small" aria-label="Cancel" title="Cancel"><i class="icon--close-thin"></i></button>
                                                    <button type="button" class="icon-button icon-button--primary icon-button--bordered icon-button--small" aria-label="Save" title="Save"><i class="icon--check"></i></button>
                                                </div>
                                            </div>
                                            <div className="simple-card__group-content"></div>
                                        </div>

                                        <small className="text-info">Folder Collapsed (note: the badge has a different style if no content inside):</small>
                                        
                                        <div className="simple-card__group">
                                            <div className="simple-card__group-header">
                                                <button type="button" class="icon-button icon-button--tertiary" title=""><i class="icon--plus"></i></button>
                                                <div className="simple-card__group-header-title">
                                                    <i class="icon--folder"></i>
                                                    <span className="simple-card__group-header-name">My New folder</span>
                                                </div>
                                                <span class="badge badge--neutral-translucent rounded-pill me-2">0</span>
                                                <div className="simple-card__group-header-actions">
                                                    <button type="button" class="icon-button icon-button--tertiary" title=""><i class="icon--more"></i></button>
                                                </div>
                                            </div>
                                            <div className="simple-card__group-content"></div>
                                        </div>

                                        <small className="text-info">On dragover:</small>
                                        
                                        <div className="simple-card__group">
                                            <div className="simple-card__group-header simple-card__group-header--ondragover">
                                                <button type="button" class="icon-button icon-button--tertiary" title=""><i class="icon--plus"></i></button>
                                                <div className="simple-card__group-header-title">
                                                    <i class="icon--folder"></i>
                                                    <span className="simple-card__group-header-name">My New folder</span>
                                                </div>
                                                <span class="badge badge--neutral-translucent rounded-pill me-2">0</span>
                                                <div className="simple-card__group-header-actions">
                                                    <button type="button" class="icon-button icon-button--tertiary" title=""><i class="icon--more"></i></button>
                                                </div>
                                            </div>
                                            <div className="simple-card__group-content"></div>
                                        </div>

                                    </div>
                                </div>

                                <EditTopic />

                            </div>
                        </section>
                    </div>
                </div>
            </div>




        </div>
    );
  }
  
  export default MyTopics;
  