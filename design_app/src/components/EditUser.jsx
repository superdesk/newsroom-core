import React from 'react';
import {useState} from 'react';

function EditUser() {
    const [isGeneralShown, setIsGeneralShown] = useState(false);
    const [isProductsShown, setIsProductsShown] = useState(false);
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
            <h3>Add/Edit User</h3>
            <button id="hide-sidebar" type="button" className="icon-button" data-dismiss="modal" aria-label="Close">
                <i className="icon--close-thin icon--gray-dark" aria-hidden="true"></i>
            </button>
        </div>
        <div className="wire-column__preview__top-bar audit-information">
            <div className="wire-column__preview__date">Created by System at 14:07 03/04/2018</div>
            <div className="wire-column__preview__date">Updated by admin admin at 09:36 20/12/2022</div>
        </div>
        <div className="list-item__preview-content">
                <div className="list-item__preview-toolbar">
                    <div>
                        <label className="label label--green label--big label--rounded">active</label>
                        <label className="label label--green label--fill label--big label--rounded">admin</label>
                    </div>
                    <button className="nh-button nh-button--tertiary nh-button--small">Resend Invite</button>
                </div>
                    <form>
                        <div className="list-item__preview-form pt-0">
                            <div className="list-item__preview-collapsible" onClick={handleClickGeneral}>
                                <div className="list-item__preview-collapsible-header">
                                    {isGeneralShown && <i className="icon--arrow-right icon--gray-dark"></i>}
                                    {!isGeneralShown && <i className="icon--arrow-right icon--gray-dark icon--rotate-90"></i>}
                                    <h3>General</h3>
                                </div>
                            </div>
                            {!isGeneralShown &&
                                <div>
                                    <div className="form-group">
                                        <label htmlFor="name">First Name<span className="text-danger">*</span></label>
                                        <div className="field">
                                            <input type="text" id="name" name="name" className="form-control" value="Jacey" />
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="name">Last Name <span className="text-danger">*</span></label>
                                        <div className="field">
                                            <input type="text" id="name" name="name" className="form-control" value="Marks" />
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="name">Email <span className="text-danger">*</span></label>
                                        <div className="field">
                                            <input type="text" id="email" name="email" className="form-control" value="jacey.marks@mycompany.com"></input>
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="name">Phone</label>
                                        <div className="field">
                                            <input type="text" id="phone" name="phone" className="form-control" value="+381 64 155 45 56"></input>
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="name">Mobile</label>
                                        <div className="field">
                                            <input type="text" id="mobile" name="mobile" className="form-control" value=""></input>
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="company">Company</label>
                                        <div className="field">
                                            <select id="company" name="company" className="form-control">
                                                <option value="My Company">My Company</option>
                                                <option value="63bc419b309f453980ce4994">663975 BC LTD (Energeticcity.ca)</option>
                                                <option value="63bc419d2a4d6027b32a8288">Akash Broadcasting Inc.</option>
                                                <option value="63bc41a1309f453980ce4998">Bhargav Corporation</option>
                                                <option value="61a8dc29fab70adfacf59789">CP</option>
                                                <option value="635ac6b9b837aa06e8e94ea3">Load Company No Exp</option>
                                                <option value="624c18f79c6bb2d7d0c6cb54">Load Test Company</option>
                                                <option value="634449a0ac2fc684e610b7f4">Nurun</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="company">Role</label>
                                        <div className="field">
                                            <select id="role" name="role" className="form-control">
                                                <option value="Admin">Admin</option>
                                                <option value="Editor">Director</option>
                                                <option value="Editor">Editor</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="name">Language</label>
                                        <div className="field">
                                            <input type="text" id="language" name="language" className="form-control" value="English"></input>
                                        </div>
                                    </div>
                                </div>
                            }
                            <div className="list-item__preview-collapsible" onClick={handleClickProducts}>
                                <div className="list-item__preview-collapsible-header">
                                    {!isProductsShown && <i className="icon--arrow-right icon--gray-dark"></i>}
                                    {isProductsShown && <i className="icon--arrow-right icon--gray-dark icon--rotate-90"></i>}
                                    <h3>Products</h3>
                                </div>
                            </div>
                            {isProductsShown &&
                                <div>
                                    <div className="list-item__preview-subheading">Wire</div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="pr1" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="pr1">Product One</label>
                                            </div>
                                        </div>
                                        <div>16/30</div>
                                    </div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="pr2" tabIndex="0" disabled></input>
                                                <label className="form-check-label" htmlFor="pr2">Product Two</label>
                                            </div>
                                        </div>
                                        <div className="text-danger">30/30</div>
                                    </div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="pr3" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="pr3">Product Three</label>
                                            </div>
                                        </div>
                                        <div>22/30</div>
                                    </div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="pr4" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="pr4">Product Four</label>
                                            </div>
                                        </div>
                                        <div>11/30</div>
                                    </div>
                                    <div className="list-item__preview-subheading">Agenda</div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="apr1" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="apr1">Product One</label>
                                            </div>
                                        </div>
                                        <div>26/30</div>
                                    </div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="apr2" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="apr2">Product Two</label>
                                            </div>
                                        </div>
                                        <div>13/30</div>
                                    </div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="apr3" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="apr3">Product Three</label>
                                            </div>
                                        </div>
                                        <div>28/30</div>
                                    </div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="apr4" tabIndex="0" disabled></input>
                                                <label className="form-check-label" htmlFor="apr4">Product Four</label>
                                            </div>
                                        </div>
                                        <div className="text-danger">30/30</div>
                                    </div>
                                </div>
                            }
                            <div className="list-item__preview-collapsible" onClick={handleClickUserSettings}>
                                <div className="list-item__preview-collapsible-header">
                                    {!isUserSettingsShown && <i className="icon--arrow-right icon--gray-dark"></i>}
                                    {isUserSettingsShown && <i className="icon--arrow-right icon--gray-dark icon--rotate-90"></i>}
                                    <h3>User Settings</h3>
                                </div>
                            </div>
                            {isUserSettingsShown &&
                                <div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="approved" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="approved">Approved</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="enabled" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="enabled">Enabled</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="cea" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="cea">Company Expiry Alert</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="list-item__preview-row">
                                        <div className="form-group">
                                            <div className="form-check">
                                                <input type="checkbox" className="form-check-input" id="mct" tabIndex="0"></input>
                                                <label className="form-check-label" htmlFor="mct">Manage Company Topics</label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            }

                        </div>
                        <div className="list-item__preview-footer">
                            <input type="button" className="nh-button nh-button--secondary" value="Reset Password" />
                            <input type="button" className="nh-button nh-button--secondary" value="Delete" />
                            <input type="button" className="nh-button nh-button--primary" value="Save" />
                        </div>
                    </form>

        </div>
    </div>
    )
}

export default EditUser;
