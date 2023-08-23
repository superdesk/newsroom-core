import * as React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';
import classNames from 'classnames';

import {gettext} from 'utils';
import {SearchResultTagList} from './SearchResultTagList';
import {Tag} from 'components/Tag';
import {IProps as IParentProps} from './SearchResultTagsList';
import {ISearchParams} from 'interfaces';

const searchTokenRegEx = /[^\s"]+|(?:"[^"]+?"(?:~[0-9]+)?)/g;

function splitTermKeywords(keywordText: string): string[] {
    const trimmedKeywordText = keywordText == null ? '' : keywordText.trim();

    if (trimmedKeywordText === '') {
        return [];
    }

    return trimmedKeywordText.match(searchTokenRegEx) || [];
}

type IProps = Pick<IParentProps,
    'readonly' |
    'searchParams' |
    'availableFields' |
    'toggleAdvancedSearchField' |
    'setAdvancedSearchKeywords' |
    'clearAdvancedSearchParams' |
    'refresh'
>;

export function SearchResultsAdvancedSearchRow({
    readonly,
    searchParams,
    availableFields,
    toggleAdvancedSearchField,
    setAdvancedSearchKeywords,
    clearAdvancedSearchParams,
    refresh,
}: IProps) {
    const advancedSearchParams: ISearchParams['advanced'] = searchParams.advanced ?? {
        all: '',
        any: '',
        exclude: '',
        fields: [],
    };

    const keywords = {
        all: splitTermKeywords(advancedSearchParams.all),
        any: splitTermKeywords(advancedSearchParams.any),
        exclude: splitTermKeywords(advancedSearchParams.exclude),
    };
    const fields = get(advancedSearchParams, 'fields') ?? [];

    if (!keywords.all.length && !keywords.any.length && !keywords.exclude.length) {
        return null;
    }

    const advancedSearchTags = [];
    const removeKeywordEntry = (field: keyof typeof keywords, index: number) => {
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
                    key={`tags-advanced--and-${index}`} // using index instead of term which might not be unique
                    text={term}
                    shade="success"
                    readOnly={readonly}
                    onClick={(event) => {
                        event.preventDefault();
                        removeKeywordEntry('all', index);
                        refresh?.();
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
                    readOnly={true}
                    onClick={(event) => {
                        event.preventDefault();
                        removeKeywordEntry('any', index);
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
                    readOnly={readonly}
                    onClick={(event) => {
                        event.preventDefault();
                        removeKeywordEntry('exclude', index);
                    }}
                />
            );
        });
    }

    if (!advancedSearchTags.length) {
        return null;
    }

    if (!readonly) {
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
                onClick={(event) => {
                    event.preventDefault();
                    clearAdvancedSearchParams();
                }}
            >
                {gettext('Clear')}
            </button>
        );
    }

    const fieldNameToLabel = {
        name: gettext('Name'),
        headline: gettext('Headline'),
        slugline: gettext('Slugline'),
        description: gettext('Description'),
        body_html: gettext('Body'),
    };

    return (
        <React.Fragment>
            <SearchResultTagList
                testId="search-results--advanced-keywords"
                title={gettext('Search for')}
                tags={advancedSearchTags}
            />
            <SearchResultTagList
                testId="search-results--advanced-fields"
                secondary={true}
                title={gettext('inside')}
            >
                <div className="toggle-button__group toggle-button__group--spaced toggle-button__group--loose">
                    {(Object.keys(fieldNameToLabel) as Array<keyof typeof fieldNameToLabel>)
                        .filter((fieldName) => availableFields.includes(fieldName))
                        .map((fieldName) => (
                            <button
                                disabled={readonly}
                                key={fieldName}
                                data-test-id={`toggle-${fieldName}-button`}
                                className={classNames(
                                    'toggle-button toggle-button--no-txt-transform toggle-button--small',
                                    {'toggle-button--active': fields.includes(fieldName)}
                                )}
                                onClick={(event) => {
                                    event.preventDefault();
                                    toggleAdvancedSearchField(fieldName);
                                    refresh?.();
                                }}
                            >
                                {fieldNameToLabel[fieldName]}
                            </button>
                        ))
                    }
                </div>
            </SearchResultTagList>
        </React.Fragment>
    );
}

SearchResultsAdvancedSearchRow.propTypes = {
    searchParams: PropTypes.object,
    availableFields: PropTypes.arrayOf(PropTypes.string).isRequired,
    toggleAdvancedSearchField: PropTypes.func.isRequired,
    setAdvancedSearchKeywords: PropTypes.func.isRequired,
    clearAdvancedSearchParams: PropTypes.func.isRequired,
};
