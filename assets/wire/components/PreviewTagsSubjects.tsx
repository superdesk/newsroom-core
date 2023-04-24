import {filterGroupsToLabelMap} from 'assets/search/selectors';
import {gettext, isDisplayed} from 'assets/utils';
import {get} from 'lodash';
import PropTypes from 'prop-types';
import React from 'react';
import {connect} from 'react-redux';
import PreviewTagsBlock from './PreviewTagsBlock';
import {PreviewTagsLinkList} from './PreviewTagsLinkList';

function PreviewTagsSubjectsComponent({subjects, displayConfig, urlPrefix, filterGroupLabels}: any) {
    if (!subjects.length) {
        return null;
    }

    const subjectsByScheme: any = {subject: []};
    const filterGroupSchemes = Object.keys(filterGroupLabels);

    subjects.forEach((subject: any) => {
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

export const PreviewTagsSubjects: any = connect(mapStateToProps)(PreviewTagsSubjectsComponent as any);
