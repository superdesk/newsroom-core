import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {gettext} from 'utils';
import {SearchResultTagList} from './SearchResultTagList';
import classNames from 'classnames';

function splitTermKeywords(keywordText) {
    const trimmedKeywordText = keywordText == null ? '' : keywordText.trim();

    return !trimmedKeywordText.length ?
        [] :
        trimmedKeywordText.split(' ');
}

export function SearchResultsAdvancedSearchRow({searchParams, toggleAdvancedSearchField, setAdvancedSearchKeywords, refresh, clearAdvancedSearchParams}) {
    const advancedSearchParams = get(searchParams, 'advanced', {});
    const keywords = {
        all: splitTermKeywords(advancedSearchParams.all),
        any: splitTermKeywords(advancedSearchParams.any),
        exclude: splitTermKeywords(advancedSearchParams.exclude),
    };
    const fields = get(advancedSearchParams, 'fields', []);

    if (!keywords.all.length && !keywords.any.length && !keywords.exclude.length) {
        return null;
    }

    const advancedSearchTags = [];
    const removeKeywordEntry = (field, index) => {
        if (keywords[field].length === 1) {
            setAdvancedSearchKeywords(field, '');
        } else {
            const newKeywords = [...keywords[field]];

            newKeywords.splice(index, 1);
            setAdvancedSearchKeywords(field, newKeywords.join(' '));
        }
    };

    if (keywords.all.length) {
        advancedSearchTags.push({text: gettext('and'), operator: true, shade: 'success', readOnly: true});

        keywords.all.forEach((term, index) => {
            advancedSearchTags.push({
                text: term,
                shade: 'success',
                onClick: () => {
                    removeKeywordEntry('all', index);
                    refresh();
                },
            });
        });
    }

    if (keywords.any.length) {
        if (advancedSearchTags.length) {
            advancedSearchTags.push('/');
        }
        advancedSearchTags.push({text: gettext('or'), operator: true, shade: 'info', readOnly: true});

        keywords.any.forEach((term, index) => {
            advancedSearchTags.push({
                text: term,
                shade: 'info',
                onClick: () => {
                    removeKeywordEntry('any', index);
                    refresh();
                },
            });
        });
    }

    if (keywords.exclude.length) {
        if (advancedSearchTags.length) {
            advancedSearchTags.push('/');
        }
        advancedSearchTags.push({text: gettext('not'), operator: true, shade: 'alert', readOnly: true});

        keywords.exclude.forEach((term, index) => {
            advancedSearchTags.push({
                text: term,
                shade: 'alert',
                onClick: () => {
                    removeKeywordEntry('exclude', index);
                    refresh();
                },
            });
        });
    }

    if (!advancedSearchTags.length) {
        return null;
    }

    return (
        <React.Fragment>
            <SearchResultTagList
                title={gettext('Search for')}
                tags={advancedSearchTags}
                buttons={[
                    <button
                        key="update_topic_button"
                        className="btn btn-outline-secondary btn-responsive btn--small"
                        onClick={clearAdvancedSearchParams}
                    >
                        {gettext('Clear')}
                    </button>
                ]}
            />
            <SearchResultTagList
                title={gettext('Fields searched')}
            >
                <div className="tags-list">
                    <button
                        className={classNames(
                            'toggle-button',
                            {'toggle-button--active': fields.includes('headline')}
                        )}
                        onClick={() => {
                            toggleAdvancedSearchField('headline');
                            refresh();
                        }}
                        style={{height: '32px'}}
                    >
                        {gettext('Headline')}
                    </button>
                    <button
                        className={classNames(
                            'toggle-button',
                            {'toggle-button--active': fields.includes('slugline')}
                        )}
                        onClick={() => {
                            toggleAdvancedSearchField('slugline');
                            refresh();
                        }}
                        style={{height: '32px'}}
                    >
                        {gettext('Slugline')}
                    </button>
                    <button
                        className={classNames(
                            'toggle-button',
                            {'toggle-button--active': fields.includes('body_html')}
                        )}
                        onClick={() => {
                            toggleAdvancedSearchField('body_html');
                            refresh();
                        }}
                        style={{height: '32px'}}
                    >
                        {gettext('Body')}
                    </button>
                </div>
            </SearchResultTagList>
        </React.Fragment>
    );
}

SearchResultsAdvancedSearchRow.propTypes = {
    searchParams: PropTypes.object,
    toggleAdvancedSearchField: PropTypes.func.isRequired,
    setAdvancedSearchKeywords: PropTypes.func.isRequired,
    refresh: PropTypes.func.isRequired,
    clearAdvancedSearchParams: PropTypes.func.isRequired,
};
