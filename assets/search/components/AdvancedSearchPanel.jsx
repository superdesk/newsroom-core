import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {gettext} from 'utils';
import {advancedSearchParamsSelector} from '../selectors';
import {toggleAdvancedSearchField, setAdvancedSearchKeywords, clearAdvancedSearchParams} from '../actions';

import CheckboxInput from 'components/CheckboxInput';
import InputWrapper from 'components/InputWrapper';

function AdvancedSearchPanelComponent({
    params,
    fetchItems,
    toggleAdvancedSearchPanel,
    toggleSearchTipsPanel,
    toggleField,
    setKeywords,
    clearParams
}) {
    return (
        <div className="advanced-search__wrapper" data-test-id="advanced-search-panel">
            <div className="advanced-search__header">
                <h3 className="a11y-only">{gettext('Advanced Search dialog')}</h3>
                <nav className="content-bar navbar">
                    <h3>{gettext('Advanced Search')}</h3>
                    <div className="btn-group">
                        <div className="mx-2">
                            <button
                                className="icon-button"
                                aria-label={gettext('Show Search Tips')}
                                onClick={toggleSearchTipsPanel}
                            >
                                <i className="icon--info" />
                            </button>
                        </div>
                        <div className="mx-2">
                            <button
                                className="icon-button icon-button icon-button--bordered"
                                aria-label={gettext('Close')}
                                onClick={toggleAdvancedSearchPanel}
                            >
                                <i className="icon--close-thin" />
                            </button>
                        </div>
                    </div>
                </nav>
            </div>
            <div className="advanced-search__content-wrapper">
                <div className="advanced-search__content">
                    <div
                        data-test-id="field-all"
                        className="advanced-search__content-block"
                    >
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold">
                            {gettext('All of these:')}
                        </p>
                        <textarea
                            name="all"
                            placeholder={gettext('keyword1 keyword2...')}
                            rows="2"
                            className="form-control"
                            value={params.all || ''}
                            onChange={(event) => setKeywords('all', event.target.value)}
                            autoFocus={true}
                        />
                        <p className="advanced-search__content-description-text">
                            {gettext('Finds every item that contains keyword1 AND keyword2 etc.')}
                        </p>
                    </div>
                    <div
                        data-test-id="field-any"
                        className="advanced-search__content-block"
                    >
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold">
                            {gettext('Any of these:')}
                        </p>
                        <textarea
                            name="any"
                            placeholder={gettext('keyword1 keyword2...')}
                            rows="2"
                            className="form-control"
                            value={params.any || ''}
                            onChange={(event) => setKeywords('any', event.target.value)}
                        />
                        <p className="advanced-search__content-description-text">
                            {gettext('And every item contain keyword1 OR keyword 2 etc.')}
                        </p>
                    </div>
                    <div
                        data-test-id="field-none"
                        className="advanced-search__content-block"
                    >
                        <p className="advanced-search__content-block-text advanced-search__content-block-text--bold">
                            {gettext('None of these:')}
                        </p>
                        <textarea
                            name="exclude"
                            placeholder={gettext('keyword1 keyword2...')}
                            rows="2"
                            className="form-control"
                            value={params.exclude || ''}
                            onChange={(event) => setKeywords('exclude', event.target.value)}
                        />
                        <p className="advanced-search__content-description-text">
                            {gettext('And every item will NOT contain keyword1 nor keyword2 etc.')}
                        </p>
                    </div>
                    <hr className="dashed" />
                    <div className="advanced-search__content-bottom">
                        <p>{gettext('Apply these keyword rules to at least one of these search fields:')}</p>
                        <InputWrapper>
                            <CheckboxInput
                                name="headline"
                                label={gettext('Headline')}
                                onChange={() => toggleField('headline')}
                                value={params.fields.includes('headline')}
                            />
                            <CheckboxInput
                                name="slugline"
                                label={gettext('Slugline')}
                                onChange={() => toggleField('slugline')}
                                value={params.fields.includes('slugline')}
                            />
                            <CheckboxInput
                                name="body_html"
                                label={gettext('Body')}
                                onChange={() => toggleField('body_html')}
                                value={params.fields.includes('body_html')}
                            />
                        </InputWrapper>
                    </div>
                </div>
            </div>
            <div className="advanced-search__footer">
                <button
                    className="nh-button nh-button--secondary"
                    onClick={() => {
                        clearParams();
                        toggleAdvancedSearchPanel();
                        fetchItems();
                    }}
                >
                    {gettext('Clear all')}
                </button>
                <button
                    data-test-id="run-advanced-search-btn"
                    className="nh-button nh-button--primary"
                    onClick={() => {
                        fetchItems();
                        toggleAdvancedSearchPanel();
                    }}
                >
                    {gettext('Search')}</button>
            </div>
        </div>
    );
}

AdvancedSearchPanelComponent.propTypes = {
    params: PropTypes.shape({
        all: PropTypes.string,
        any: PropTypes.string,
        exclude: PropTypes.string,
        fields: PropTypes.arrayOf(PropTypes.string)
    }),
    fetchItems: PropTypes.func,
    toggleAdvancedSearchPanel: PropTypes.func,
    toggleSearchTipsPanel: PropTypes.func,
    toggleField: PropTypes.func,
    setKeywords: PropTypes.func,
    clearParams: PropTypes.func,
};

const mapStateToProps = (state) => ({
    params: advancedSearchParamsSelector(state),
});

const mapDispatchToProps = (dispatch) => ({
    toggleField: (field) => dispatch(toggleAdvancedSearchField(field)),
    setKeywords: (field, keywords) => dispatch(setAdvancedSearchKeywords(field, keywords)),
    clearParams: () => dispatch(clearAdvancedSearchParams()),
});


export const AdvancedSearchPanel = connect(mapStateToProps, mapDispatchToProps)(AdvancedSearchPanelComponent);
