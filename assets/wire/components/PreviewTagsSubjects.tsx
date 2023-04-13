import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';

import {gettext, isDisplayed} from 'utils';
import {filterGroupsToLabelMap} from 'search/selectors';

import PreviewTagsBlock from './PreviewTagsBlock';
import {PreviewTagsLinkList} from './PreviewTagsLinkList';


function PreviewTagsSubjectsComponent({subjects, displayConfig, urlPrefix, filterGroupLabels}) {
    if (!subjects.length) {
        return null;
    }

    const subjectsByScheme = {subject: []};
    const filterGroupSchemes = Object.keys(filterGroupLabels);

    subjects.forEach((subject) => {
        if (subject.scheme && filterGroupSchemes.includes(subject.scheme)) {
            if (subjectsByScheme[subject.scheme] == null) {
                subjectsByScheme[subject.scheme] = [];
            }

            subjectsByScheme[subject.scheme].push(subject);
        } else {
            subjectsByScheme.subject.push(subject);
        }
    });

    const schemesToDisplay = Object.keys(subjectsByScheme)
        .filter((scheme) => (
            subjectsByScheme[scheme].length > 0 &&
            isDisplayed(scheme === 'subject' ? 'subjects' : scheme, displayConfig))
        );

    return !schemesToDisplay.length ? null : schemesToDisplay.map((scheme) => (
        <PreviewTagsBlock
            key={scheme}
            label={get(filterGroupLabels, scheme, gettext('Subject'))}
        >
            <PreviewTagsLinkList
                urlPrefix={urlPrefix}
                items={subjectsByScheme[scheme]}
                field={scheme}
            />
        </PreviewTagsBlock>
    ));
}

PreviewTagsSubjectsComponent.propTypes = {
    subjects: PropTypes.array,
    displayConfig: PropTypes.object,
    urlPrefix: PropTypes.string,
    filterGroupLabels: PropTypes.object,
};

const mapStateToProps = (state: any) => ({
    filterGroupLabels: filterGroupsToLabelMap(state),
});

export const PreviewTagsSubjects = connect(mapStateToProps)(PreviewTagsSubjectsComponent);
