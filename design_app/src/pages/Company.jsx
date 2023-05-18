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
                        <button onClick={handleClickNav} className="icon-button icon-button--border-three-sides" aria-label="Open Side Navigation">
                        {!isCompanyNavShown && <i className="icon--hamburger icon--gray"></i>}
                        {isCompanyNavShown && <i className="icon--arrow-right icon--rotate-180 icon--gray"></i>}
                        </button>

                        <div className="btn-group btn-group--navbar">
                            <button onClick={handleSetActive} className={isActive ? 'btn btn-outline-primary active' : 'btn btn-outline-primary'}>My Company</button>
                            <button onClick={handleSetActive} className={!isActive ? 'btn btn-outline-primary active' : 'btn btn-outline-primary'}>Users</button>                            
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
                        <div className="search d-flex align-items-center">
                            <span className="search__icon">
                                <i className="icon--search icon--gray"></i>
                            </span>
                            <div className="search__form input-group">
                                <form className="d-flex align-items-center" role="search" aria-label="search"><input type="text" name="q" className="search__input form-control" placeholder="Search for..." aria-label="Search for..." />
                                    <div className="search__form__buttons">
                                        <button className="btn search__clear" aria-label="Search clear" type="reset"><img src="src/assets/images/search_clear.png" width="16" height="16" /></button>
                                        <button className="btn btn-outline-secondary" type="submit">Search</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                        <div className="content-bar__right">
                            <button onClick={handleClickEdit} className="btn btn-outline-secondary btn-responsive">Add User</button>
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
  