import React from 'react';
import {useState} from 'react';

function EditTopic() {
    const [isGeneralShown, setIsGeneralShown] = useState(true);
    const [isProductsShown, setIsProductsShown] = useState(true);
    const [isUserSettingsShown, setIsUserSettingsShown] = useState(false);

    const handleClickGeneral = event => {
        setIsGeneralShown(current => !current);
    };
    const handleClickProducts = event => {
        setIsProductsShown(current => !current);
    };
    const handleClickUserSettings = event => {
        setIsUserSettingsShown(current => !current);
    };

    return (
        <div className="list-item__preview" role="dialog" aria-label="Edit Company">
            <div className="list-item__preview-header">
                <h3>Edit Topic</h3>
                <button id="hide-sidebar" type="button" className="icon-button" data-dismiss="modal" aria-label="Close">
                    <i className="icon--close-thin icon--gray-dark" aria-hidden="true"></i>
                </button>
            </div>
            <div className="wire-column__preview__top-bar audit-information">
                <div className="wire-column__preview__date">Created by System at 14:07 03/04/2018</div>
                <div className="wire-column__preview__date">Updated by admin admin at 09:36 20/12/2022</div>
            </div>
            <div className="list-item__preview-content">
                    <form>
                        <div className="nh-flex-container list-item__preview-form pt-0">
                            <div className="nh-flex__row">
                                <div className="nh-flex__column">
                                    <div className="form-group" data-test-id="field-undefined">
                                        <label>Name <span className="text-danger">*</span></label>
                                        <div className="field">
                                            <input type="text" className="form-control" required="" maxLength="30" value="My Ukraine War Topic" />
                                        </div>
                                    </div>
                                    <div className="form-check" tabIndex="-1" data-test-id="field-input-Share with my Company">
                                        <input type="checkbox" name="input-Share with my Company" className="form-check-input" id="input-Share with my Company" tabIndex="0" />
                                        <label className="form-check-label" htmlFor="input-Share with my Company">Share with my Company</label>
                                    </div>

                                </div>
                            </div>

                            <div className="nh-flex__row">
                                <div className="nh-flex__column">
                                    <div className="list-item__preview-collapsible" onClick={handleClickGeneral}>
                                        <div className="list-item__preview-collapsible-header">
                                            {!isGeneralShown && <i className="icon--arrow-right icon--gray-dark"></i>}
                                            {isGeneralShown && <i className="icon--arrow-right icon--rotate-90"></i>}
                                            <h3>Email Notifications</h3>
                                        </div>
                                    </div>
                                    {isGeneralShown &&
                                        <div>
                                            <div className="toggle-button__group toggle-button__group--spaced toggle-button__group--stretch-items my-2">
                                                <button className="toggle-button toggle-button--small">None</button>
                                                <button className="toggle-button toggle-button--small">Real-Time</button>
                                                <button className="toggle-button toggle-button--small toggle-button--active">Scheduled</button>
                                            </div>
                                            <div className="nh-container nh-container--highlight mb-3">
                                                <p className="nh-container__text--small">Your saved topic results will be emailed in a digest format at the time(s) per day set below.</p>
                                                <div className="h-spacer h-spacer--medium"></div>
                                                <span className="nh-container__schedule-info mb-3">Daily @ 07:00 AM, 03:00 PM and 07:00 PM, EST</span>
                                                <button type="button" className="nh-button nh-button--small nh-button--tertiary" title="">Edit schedule</button>
                                            </div>
                                        </div>
                                    }
                                </div>
                                <div className="nh-flex__column">
                                    <div className="list-item__preview-collapsible" onClick={handleClickProducts}>
                                        <div className="list-item__preview-collapsible-header">
                                            {!isProductsShown && <i className="icon--arrow-right"></i>}
                                            {isProductsShown && <i className="icon--arrow-right icon--rotate-90"></i>}
                                            <h3>Organize your Topic</h3>
                                        </div>
                                    </div>
                                    {isProductsShown &&
                                        <div>
                                            <div className="nh-container nh-container--direction-row mb-3 pt-2 pb-3">
                                                <div className="dropdown">
                                                    <button type="button" className="nh-dropdown-button nh-dropdown-button--stretch nh-dropdown-button--small" aria-haspopup="true" aria-expanded="false">
                                                        <i className="icon--folder"></i>
                                                        <span className="nh-dropdown-button__text-label">Add to folder</span>
                                                        <i className="nh-dropdown-button__caret icon-small--arrow-down"></i>
                                                    </button>
                                                    <div className="dropdown-menu">
                                                        <span type="button" className="dropdown-item">Sort By</span>
                                                        <div className="dropdown-divider"></div>
                                                        <button className="dropdown-item" disabled="">First Name</button>
                                                        <button className="dropdown-item">Last Name</button>
                                                        <button className="dropdown-item">Last Active</button>
                                                        <button className="dropdown-item">Date Created</button>
                                                        <button className="dropdown-item">User Type</button>
                                                        <button className="dropdown-item">User Status</button>
                                                    </div>
                                                </div>
                                            </div>
                                            <small className="text-info">When creating a new folder:</small>
                                            <div className="nh-container nh-container--direction-row mb-3 pt-2 pb-3">
                                                <div className="d-flex flex-row flex-grow-1 align-items-center gap-2 ps-1">
                                                    <i className="icon--folder icon--small"></i>
                                                    <input type="text" aria-label="Folder name" className="form-control form-control--small" maxLength="30" value="My New folder" />
                                                    <button type="button" className="icon-button icon-button--secondary icon-button--bordered icon-button--small" aria-label="Cancel" title="Cancel"><i className="icon--close-thin"></i></button>
                                                    <button type="button" className="icon-button icon-button--primary icon-button--bordered icon-button--small" aria-label="Save" title="Save"><i className="icon--check"></i></button>
                                                </div>
                                            </div>
                                            <small className="text-info">When a folder is already selected:</small>
                                            <div className="nh-container nh-container--direction-row mb-3 pt-2 pb-3">
                                                <div className="dropdown">
                                                    <button type="button" className="nh-dropdown-button nh-dropdown-button--stretch nh-dropdown-button--small" aria-haspopup="true" aria-expanded="false">
                                                        <i className="icon--folder"></i>
                                                        My New folder
                                                        <i className="nh-dropdown-button__caret icon-small--arrow-down"></i>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    }

                                </div>
                            </div>

                            <div className="nh-flex__row">
                                <div className="nh-flex__column">
                                    <div className="list-item__preview-collapsible" onClick={handleClickUserSettings}>
                                        <div className="list-item__preview-collapsible-header">
                                            {!isUserSettingsShown && <i className="icon--arrow-right"></i>}
                                            {isUserSettingsShown && <i className="icon--arrow-right icon--rotate-90"></i>}
                                            <h3>Topic details</h3>
                                        </div>
                                    </div>
                                    {isUserSettingsShown &&
                                        <div>
                                            <ul className="search-result__tags-list">
                                                <li className="search-result__tags-list-row">
                                                    <span className="search-result__tags-list-row-label">Searched for</span>
                                                    <div className="tags-list">
                                                        <span className="tag-label tag-label--read-only">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">Donetsk</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                    </div>
                                                </li>
                                                <li className="search-result__tags-list-row">
                                                    <span className="search-result__tags-list-row-label">Searched for</span>
                                                    <div className="tags-list">

                                                        <span className="tag-label tag-label--operator tag-label--success">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">and</span>
                                                            </span>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only tag-label--success">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">Russia</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only tag-label--success">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">War</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>

                                                        <span className="tag-list__separator"></span>

                                                        <span className="tag-label tag-label--operator tag-label--info">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">or</span>
                                                            </span>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only tag-label--info">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">Zelensky</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only tag-label--info">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">Peace</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>

                                                        <span className="tag-list__separator"></span>

                                                        <span className="tag-label tag-label--operator tag-label--alert">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">not</span>
                                                            </span>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only tag-label--alert">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">Trufeau</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only tag-label--alert">
                                                            <span className="tag-label--text-wrapper">
                                                                <span className="tag-label--text">Bomb</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                    </div>
                                                </li>
                                                <li className="search-result__tags-list-row">
                                                    <span className="search-result__tags-list-row-label">Fields searched</span>
                                                    <div className="toggle-button__group toggle-button__group--spaced toggle-button__group--loose">
                                                        <button className="toggle-button toggle-button--no-txt-transform toggle-button--small toggle-button--active" disabled>Headline</button>
                                                        <button className="toggle-button toggle-button--no-txt-transform toggle-button--small toggle-button--active" disabled>Slugline</button>
                                                        <button className="toggle-button toggle-button--no-txt-transform toggle-button--small" disabled>Body</button>
                                                    </div>
                                                </li>
                                                <li className="search-result__tags-list-row">
                                                    <span className="search-result__tags-list-row-label">Filters applied</span>
                                                    <div className="tags-list">
                                                        <span className="tag-label tag-label--read-only">
                                                            <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Source:</span>
                                                                <span className="tag-label--text">Cision</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only">
                                                            <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Category:</span>
                                                                <span className="tag-label--text">Politics</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only">
                                                            <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">From:</span>
                                                                <span className="tag-label--text">Feb 1st,2023</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only">
                                                            <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">To:</span>
                                                                <span className="tag-label--text">Mar 1st,2023</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only">
                                                            <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Subject:</span>
                                                                <span className="tag-label--text">Affairs</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only">
                                                            <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Ranking:</span>
                                                                <span className="tag-label--text">2</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                        <span className="tag-label tag-label--read-only">
                                                            <span className="tag-label--text-wrapper">
                                                            <span className="tag-label--text-label">Version:</span>
                                                                <span className="tag-label--text">2</span>
                                                            </span>
                                                            <button className="tag-label__remove">
                                                                <i className="icon--close-thin"></i>
                                                            </button>
                                                        </span>
                                                    </div>
                                                </li>
                                                <li id="editButtonRow" className="search-result__tags-list-row">
                                                    <div className="tags-list">
                                                        <button type="button" className="nh-button nh-button--small nh-button--tertiary" title="">Edit search terms</button>
                                                    </div>
                                                </li>
                                            </ul>
                                        </div>
                                    }
                                </div>
                            </div>



                            <div className="h-spacer h-spacer--blanc h-spacer--small"></div>

                        </div>
                    </form>

            </div>
            <div className="list-item__preview-footer">
                <input type="button" className="nh-button nh-button--secondary" value="Cancel" />
                <input type="button" className="nh-button nh-button--primary" value="Save" />
            </div>
    </div>
    )
}

export default EditTopic;
