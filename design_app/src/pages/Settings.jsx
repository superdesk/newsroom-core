import React from 'react';
//import { useNavigate } from 'react-router-dom';

function Settings() { 
    return (
        <div className="settingsWrap">
            <div className="settings-inner">
                <div className="side-navigation" id="settings-menu">
                    <h3 className="a11y-only">Settings Menu</h3>
                    <ul>
                        <li>
                            <a className="side-navigation__btn active" href="/settings/companies">
                                Company Management</a>
                        </li>
                        <li>
                            <a className="side-navigation__btn " href="/settings/oauth_clients">
                                OAuth Clients</a>
                        </li>                
                        <li>
                            <a className="side-navigation__btn " href="/settings/users">
                                User Management</a>
                        </li>
                        <li>
                            <a className="side-navigation__btn " href="/settings/monitoring">
                                Monitoring</a>
                        </li>
                        <li>
                            <a className="side-navigation__btn " href="/settings/navigations">
                                Global Topics</a>
                        </li>
                        <li>
                            <a className="side-navigation__btn " href="/settings/products">
                                Products</a>
                        </li>
                        <li>
                            <a className="side-navigation__btn " href="/settings/section-filters">
                                Section Filters</a>
                        </li>
                        <li>
                            <a className="side-navigation__btn " href="/settings/cards">
                                Dashboards</a>
                        </li>
                        <li>
                            <a className="side-navigation__btn " href="/settings/general-settings">
                                General Settings</a>
                        </li>
                    </ul>
                </div>
            <div className="content">
                <section className="content-header">
                    <nav className="content-bar navbar content-bar--side-padding">
                        <div className="search d-flex align-items-center">
                            <span className="search__icon"><i className="icon--search icon--gray"></i></span>
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
                            <button className="btn btn-outline-secondary btn-responsive">New Company</button>
                        </div>
                    </nav>
                </section>

                <div className="flex-row">
                    <div className="flex-col flex-column">
                        <section className="content-main">
                            <div className="list-items-container">
                                <table className="table table-hover" tabIndex="-1">
                                    <thead>
                                        <tr>
                                            <th>Name</th>
                                            <th>Type</th>
                                            <th>Account Manager</th>
                                            <th>Status</th>
                                            <th>Contact</th>
                                            <th>Telephone</th>
                                            <th>Country</th>
                                            <th>Created On</th>
                                            <th>Expires On</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr className="" tabIndex="0">
                                            <td className="name">Awesome company</td>
                                            <td className="type"></td>
                                            <td></td>
                                            <td>Enabled</td>
                                            <td>Antonin Dvorak</td>
                                            <td>+776766766</td>
                                            <td>Finland</td>
                                            <td>03/04/2018</td>
                                            <td></td>
                                        </tr>
                                        <tr className="" tabIndex="0">
                                            <td className="name">Company to expire</td>
                                            <td className="type"></td>
                                            <td></td>
                                            <td className="text-danger">Enabled</td>
                                            <td></td>
                                            <td></td>
                                            <td>Finland</td>
                                            <td>09/02/2022</td>
                                            <td>10/02/2022</td>
                                        </tr>
                                        <tr className="" tabIndex="0">
                                            <td className="name">EXP comp</td>
                                            <td className="type"></td>
                                            <td></td>
                                            <td className="text-danger">Enabled</td>
                                            <td></td>
                                            <td></td>
                                            <td>Finland</td>
                                            <td>18/02/2022</td>
                                            <td>19/02/2022</td>
                                        </tr>
                                        <tr className="" tabIndex="0">
                                            <td className="name">NBN-yhtiö</td>
                                            <td className="type"></td>
                                            <td></td>
                                            <td>Enabled</td>
                                            <td></td>
                                            <td></td>
                                            <td>Finland</td>
                                            <td>27/11/2020</td>
                                            <td></td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </section>
                    </div>

                    
                    <div className="list-item__preview" role="dialog" aria-label="Edit Company">
                        <div className="list-item__preview-header">
                            <h3>Awesome company</h3>
                            <button id="hide-sidebar" type="button" className="icon-button" data-dismiss="modal" aria-label="Close">
                                <i className="icon--close-thin icon--gray-dark" aria-hidden="true"></i>
                            </button>
                        </div>
                        <div className="wire-column__preview__top-bar pt-0 audit-information pt-2">
                            <div className="wire-column__preview__date">Created by System at 14:07 03/04/2018</div>
                            <div className="wire-column__preview__date">Updated by admin admin at 09:36 20/12/2022</div>
                        </div>
                        <ul className="nav nav-tabs">
                            <li className="nav-item">
                                <a name="company-details" className="nav-link active" href="#">Company</a>
                            </li>
                            <li className="nav-item">
                                <a name="users" className="nav-link false" href="#">Users</a>
                            </li>
                            <li className="nav-item">
                                <a name="permissions" className="nav-link false" href="#">Permissions</a>
                            </li>
                        </ul>
                        <div className="tab-content">
                            <div className="tab-pane active" id="company-details">
                                <form>
                                    <div className="list-item__preview-form">
                                        <div className="form-group">
                                            <label for="name">Name</label>
                                            <div className="field">
                                                <input type="text" id="name" name="name" className="form-control" value="Awesome company" />
                                            </div>
                                        </div>
                                        <div className="form-group">
                                        <label for="company_type">Company Type</label>
                                        <div className="field">
                                            <select id="company_type" name="company_type" className="form-control">
                                                <option value=""></option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label for="url">Company Url</label>
                                        <div className="field">
                                            <input type="text" id="url" name="url" className="form-control" value="www.awesome.com" />
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label for="sd_subscriber_id">Superdesk Subscriber Id</label>
                                        <div className="field">
                                            <input type="text" id="sd_subscriber_id" name="sd_subscriber_id" className="form-control" value="899998767" />
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label for="account_manager">Account Manager</label>
                                        <div className="field">
                                            <input type="text" id="account_manager" name="account_manager" className="form-control" value="" />
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label for="phone">Telephone</label>
                                        <div className="field">
                                            <input type="text" id="phone" name="phone" className="form-control" value="+776766766" />
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label for="contact_name">Contact Name</label>
                                        <div className="field">
                                            <input type="text" id="contact_name" name="contact_name" className="form-control" value="Antonin Dvorak" />
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label for="contact_email">Contact Email</label>
                                        <div className="field">
                                            <input type="text" id="contact_email" name="contact_email" className="form-control" value="dvorak@awesome.com" />
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label for="country">Country</label>
                                        <div className="field">
                                            <select id="country" name="country" className="form-control">
                                                <option value="au">Australia</option>
                                                <option value="nz">New Zealand</option>
                                                <option value="fin">Finland</option>
                                                <option value="other">Other</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label for="expiry_date">Expiry Date</label>
                                        <div className="field">
                                            <input type="date" id="expiry_date" name="expiry_date" className="form-control" value="" />
                                        </div>
                                    </div>
                                    <div className="form-check p-0">
                                        <div className="form-check" tabIndex="-1">
                                            <input type="checkbox" name="is_enabled" className="form-check-input" id="is_enabled" tabIndex="0" checked="" />
                                            <label className="form-check-label" for="is_enabled">Enabled</label>
                                        </div>
                                    </div>
                                    </div>
                                    <div className="list-item__preview-footer">
                                        <input type="button" className="btn btn-outline-primary" value="Save" /><input type="button" className="btn btn-outline-secondary" value="Delete" />
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                        


                </div>

            </div>
            </div>

        </div>
    );
  }
  
  export default Settings;
  