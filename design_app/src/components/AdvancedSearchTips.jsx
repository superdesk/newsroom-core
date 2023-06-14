import React from 'react';

function AdvancedSearchTips() {
    return (
        <div className="advanced-search__wrapper">
            <div className="advanced-search__header">
                <h3 className="a11y-only">Advanced Search Tips dialog</h3>
                <nav className="content-bar navbar">
                    <h3>Tips</h3>
                    <div className="btn-group">
                        <div className="mx-2">
                            <button className="icon-button icon-button icon-button--bordered" aria-label="Info"><i className="icon--close-thin"></i></button>
                        </div>
                    </div>
                </nav>
                <div className="advanced-search__subnav-wrapper">
                    <div className="advanced-search__subnav-content">
                        <ul className="nav nav-tabs nav-tabs--light">
                            <li className="nav-item"><a name="company-details" className="nav-link" href="#">Regular search</a></li>
                            <li className="nav-item">
                                <a name="users" className="nav-link active" href="#">Advanced search</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            <div className="advanced-search__content-wrapper">
                <div className="advanced-search__content">
                    <div className="advanced-search__content-block advanced-search__content-block--no-background">
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor:</p>
                    </div>
                    <div className="advanced-search__content-block advanced-search__content-block--no-background">
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold"><span className="blue">Can contain</span> any of these words:</p>
                        <ul>
                            <li>This is the classic “OR” operator</li>
                            <li>Not every word you include needs to be present in the results</li>
                            <li>This is the most broad search type</li>
                            <li>Including too many terms may return too many, less relevant search results</li>
                        </ul>
                        <p className="advanced-search__content-description-text">
                            Example: Find results that include “Apples” OR “Pears” OR “Bananas”
                        </p>
                    </div>
                    <hr className="dashed" />
                    <div className="advanced-search__content-block advanced-search__content-block--no-background">
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold"><span className="green">Must contain</span> all of these words:</p>
                        <ul>
                            <li>This is the classic “AND” operator</li>
                            <li>Every word you include must be present in the results</li>
                            <li>This is a more restrictive search type</li>
                            <li>Including too many terms may return too few search results</li>
                        </ul>
                        <p className="advanced-search__content-description-text">
                            Example: Find results that include “Apples” AND “Pears” AND “Bananas”
                        </p>
                    </div>
                    <hr className="dashed" />
                    <div className="advanced-search__content-block advanced-search__content-block--no-background">
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold"><span className="red">Must not contain</span> any of these words:</p>
                        <ul>
                            <li>This is the classic “NOT” operator</li>
                            <li>Every word you include must not be present in the results</li>
                            <li>This is the most restrictive search type</li>
                            <li>Use this in combination with other keywords and operators to narrow search results</li>
                        </ul>
                        <p className="advanced-search__content-description-text">
                        Example: Find results that include “Apples” OR “Pear”s, but NOT “Bananas”
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default AdvancedSearchTips;
