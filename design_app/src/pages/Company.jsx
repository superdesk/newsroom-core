import React from 'react';
import CompanyNav from '../components/CompanyNav';
import EditUser from '../components/EditUser';
import Users from '../components/Users';
import MyCompany from '../components/MyCompany';
import {useState} from 'react';

function Company() {

    const [isCompanyNavShown, setIsCompanyNavShown] = useState(false);
    const [isEditCompanyShown, setIsEditCompanyShown] = useState(false);
    const [isActive, setIsActive] = useState(false);

    const handleClickNav = event => {
        setIsCompanyNavShown(current => !current);
    };
    const handleClickEdit = event => {
        setIsEditCompanyShown(current => !current);
    };
    const handleSetActive = event => {
        setIsActive(current => !current);
    }

    return (
        <div className="settingsWrap">
            <div className="settings-inner">
                {isCompanyNavShown && <CompanyNav />}
            <div className="content">
                <section className="content-header">                    
                    <nav className="content-bar navbar content-bar--no-left-padding">
                        {/* <button onClick={handleClickNav} className="icon-button icon-button--border-three-sides" aria-label="Open Side Navigation">
                        {!isCompanyNavShown && <i className="icon--hamburger icon--gray"></i>}
                        {isCompanyNavShown && <i className="icon--arrow-right icon--rotate-180 icon--gray"></i>}
                        </button> */}

                        <div className="toggle-button__group toggle-button__group--navbar">
                            <button onClick={handleSetActive} className={isActive ? 'toggle-button toggle-button--active' : 'toggle-button'}>My Company</button>
                            <button onClick={handleSetActive} className={!isActive ? 'toggle-button toggle-button--active' : 'toggle-button'}>Users</button>                                                      
                        </div>
                        
                        <div className="btn-group">
                            <button id="company" type="button" className="btn btn-text-only d-flex btn-sm" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                Product one<span>6/10</span>
                                <i className="icon-small--arrow-down icon--gray-dark"></i>
                            </button>                            
                        </div>
                        <div className="content-bar-divider"></div>
                        <div className="btn-group">
                            <button id="company" type="button" className="btn btn-text-only d-flex btn-sm" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                <span>Sort by:</span>Last active
                                <i className="icon-small--arrow-down icon--gray-dark"></i>
                            </button>
                        </div>
                        <div className="btn-group">
                            <button className="icon-button" aria-label="Sort"><i className="icon--filter icon--gray-dark"></i></button>
                        </div>
                        <div className="content-bar-divider"></div>

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
                            <button onClick={handleClickEdit} className="nh-button nh-button--primary">Add User</button>
                        </div>
                    </nav>
                </section>

                <div className="flex-row">
                    <div className="flex-col flex-column">
                        <section className="content-main">
                            <div className="list-items-container">
                                {!isActive && <Users />}
                                {isActive && <MyCompany />}
                            </div>
                        </section>
                    </div>
                    {!isEditCompanyShown && <EditUser />}                    
                </div>

            </div>
            </div>

        </div>
    );
  }
  
  export default Company;
  