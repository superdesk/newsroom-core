import React from 'react';

function AdvancedSearch() {
    return (
        <div className="advanced-search__wrapper">
            <div className="advanced-search__header">
                <h3 className="a11y-only">Advanced Search dialog</h3>
                <nav className="content-bar navbar">
                    <h3>Advanced Search</h3>
                    <div className="btn-group">
                        <div className="mx-2">
                            <button className="icon-button" aria-label="Info"><i className="icon--info"></i></button>
                        </div>
                        <div className="mx-2">
                            <button className="icon-button icon-button icon-button--bordered" aria-label="Close"><i className="icon--close-thin"></i></button>
                        </div>
                    </div>
                </nav>
            </div>
            <div className="advanced-search__content-wrapper">
                <div className="advanced-search__content">
                    <div className="advanced-search__content-block">
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold"><span className="blue">Can contain</span> any of these words:</p>
                        <textarea name="" id="" placeholder="Add words here..." rows="2" className="form-control"></textarea>
                        <p className="advanced-search__content-description-text">You are searching Trudeau OR Russia OR Biden</p>
                    </div>
                    <div className="advanced-search__content-block">
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold"><span className="green">Must contain</span> all of these words:</p>
                        <textarea name="" id="" placeholder="Add words here..." rows="2" className="form-control"></textarea>
                        <p className="advanced-search__content-description-text">You are searching Ukraine AND Zelensky AND Peace</p>
                    </div>
                    <div className="advanced-search__content-block">
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold"><span className="red">Must not contain</span> any of these words:</p>
                        <textarea name="" id="" placeholder="Add words here..." rows="2" className="form-control"></textarea>
                        <p className="advanced-search__content-description-text">You are excluding for your search Bomb AND War</p>
                    </div>
                    <hr className="dashed" />
                    <div className="advanced-search__content-bottom">
                        <p>Apply these keyword rules to these text fields:</p>
                        <div className="form-group">
                            <div className="form-check">
                                <input type="checkbox" className="form-check-input" id="headline" tabIndex="0" />
                                <label className="form-check-label" htmlFor="headline">Headline</label>
                            </div>
                            <div className="form-check">
                                <input type="checkbox" className="form-check-input" id="slugline" tabIndex="0" />
                                <label className="form-check-label" htmlFor="slugline">Slugline</label>
                            </div>
                            <div className="form-check">
                                <input type="checkbox" className="form-check-input" id="body" tabIndex="0" />
                                <label className="form-check-label" htmlFor="body">Body</label>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="advanced-search__footer">
                    <button className="btn btn-outline-secondary">Clear all</button>
                    <button className="btn btn-primary">Search</button>
            </div>
        </div>
    )
}

export default AdvancedSearch;
