import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import classNames from 'classnames';

import {gettext} from 'utils';
import {SearchResultTagList} from './SearchResultTagList';
import {Tag} from 'components/Tag';

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
        advancedSearchTags.push(
            <Tag
                key="tags-advanced--and"
                text={gettext('and')}
                operator={true}
                shade="success"
                readOnly={true}
            />
        );

        keywords.all.forEach((term, index) => {
            advancedSearchTags.push(
                <Tag
                    key={`tags-advanced--and-${term}`}
                    text={term}
                    shade="success"
                    onClick={() => {
                        removeKeywordEntry('all', index);
                        refresh();
                    }}
                />
            );
        });
    }

    if (keywords.any.length) {
        if (advancedSearchTags.length) {
            advancedSearchTags.push(
                <span
                    key="tag-advanced--separator-any"
                    className="tag-list__separator"
                />
            );
        }

        advancedSearchTags.push(
            <Tag
                key="tags-advanced--or"
                text={gettext('or')}
                operator={true}
                shade="info"
                readOnly={true}
            />
        );

        keywords.any.forEach((term, index) => {
            advancedSearchTags.push(
                <Tag
                    key={`tags-advanced--or-${term}`}
                    text={term}
                    shade="info"
                    onClick={() => {
                        removeKeywordEntry('any', index);
                        refresh();
                    }}
                />
            );
        });
    }

    if (keywords.exclude.length) {
        if (advancedSearchTags.length) {
            advancedSearchTags.push(
                <span
                    key="tag-separator--exclude"
                    className="tag-list__separator"
                />
            );
        }
        advancedSearchTags.push(
            <Tag
                key="tags-advanced--exclude"
                text={gettext('not')}
                operator={true}
                shade="alert"
                readOnly={true}
            />
        );

        keywords.exclude.forEach((term, index) => {
            advancedSearchTags.push(
                <Tag
                    key={`tags-advanced--exclude-${term}`}
                    text={term}
                    shade="alert"
                    onClick={() => {
                        removeKeywordEntry('exclude', index);
                        refresh();
                    }}
                />
            );
        });
    }

    if (!advancedSearchTags.length) {
        return null;
    }

    advancedSearchTags.push(
        <span
            key="tag-separator--clear"
            className="tag-list__separator tag-list__separator--blanc"
        />
    );
    advancedSearchTags.push(
        <button
            key="tag-clear-button"
            className='nh-button nh-button--tertiary nh-button--small'
            onClick={() => {
                clearAdvancedSearchParams();
                refresh();
            }}
        >
            {gettext('Clear')}
        </button>
    );

    return (
        <React.Fragment>
            <SearchResultTagList
                testId="search-results--advanced-keywords"
                title={gettext('Search for')}
                tags={advancedSearchTags}
            />
            <SearchResultTagList
                testId="search-results--advanced-fields"
                title={gettext('Fields searched')}
            >
                <div className="toggle-button__group toggle-button__group--spaced toggle-button__group--loose">
                    <button
                        data-test-id="toggle-headline-button"
                        className={classNames(
                            'toggle-button toggle-button--no-txt-transform toggle-button--small',
                            {'toggle-button--active': fields.includes('headline')}
                        )}
                        onClick={() => {
                            toggleAdvancedSearchField('headline');
                            refresh();
                        }}
                    >
                        {gettext('Headline')}
                    </button>
                    <button
                        data-test-id="toggle-slugline-button"
                        className={classNames(
                            'toggle-button toggle-button--no-txt-transform toggle-button--small',
                            {'toggle-button--active': fields.includes('slugline')}
                        )}
                        onClick={() => {
                            toggleAdvancedSearchField('slugline');
                            refresh();
                        }}
                    >
                        {gettext('Slugline')}
                    </button>
                    <button
                        data-test-id="toggle-body-button"
                        className={classNames(
                            'toggle-button toggle-button--no-txt-transform toggle-button--small',
                            {'toggle-button--active': fields.includes('body_html')}
                        )}
                        onClick={() => {
                            toggleAdvancedSearchField('body_html');
                            refresh();
                        }}
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
