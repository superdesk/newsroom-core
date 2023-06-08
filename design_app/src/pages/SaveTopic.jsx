import React from 'react';
import EditTopic from '../components/EditTopic';

function SaveTopic() {
    return (
        <div id="user-profile-app" className="settingsWrap">
            <div className="profile-container" role='dialog' aria-label="Save Topics">
                <div className="profileWrap">
                    <div className="profile__mobile-close d-md-none">
                        <button className="icon-button" aria-label='Close' onClick={'/wire'}>
                            <i className="icon--close-thin icon--gray-dark" />
                        </button>
                    </div>
                    <nav className='profile-side-navigation' id='profile-menu'>
                        <div className="profile__group">
                            <figure className="profile__avatar initials">
                                <span className="profile__characters">JL</span>
                            </figure>
                            <div className="profile__name-container">
                                <h5 className="profile__name">Jeffrey Lebowski</h5>
                            </div>
                        </div>
                        <div className="profile-side-navigation__items">
                            <a href="#" className="btn w-100 btn-outline-secondary" name="profile">My Profile</a>
                            <a href="#" className="btn w-100 btn-outline-primary" name="topics">My Wire Topics</a>
                            <a href="#" className="btn w-100 btn-outline-secondary" name="events">My Agenda Topics</a>
                        </div>
                    </nav>
                    <div className="content">
                        <section className="content-header">
                            <nav className="profile-nav content-bar navbar content-bar--side-padding pe-0 d-none d-md-flex">
                                <h5 className="ps-xl-4 mb-0">
                                    Save Topics
                                </h5>
                                <div className="content-bar__right">
                                    <button className="content-bar__menu" aria-label='Close' role="button">
                                        <i className="icon--close-thin" />
                                    </button>
                                </div>
                            </nav>
                        </section>
                        <section className="content-main">
                            <div className="profile-content profile-content--save-topic">
                                <EditTopic />
                            </div>
                        </section>
                    </div>
                </div>
            </div>




        </div>
    );
  }
  
  export default SaveTopic;
  