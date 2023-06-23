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
                                Save Topics
                            </h5>
                            <button className="profile__profile-content-close" aria-label='Close' role="button">
                                <i className="icon--close-thin" />
                            </button>
                        </section>
                        <section className="profile__profile-content-main">
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
  