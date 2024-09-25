import * as React from 'react';
import moment from 'moment';

import {IAgendaItem} from 'interfaces';
import {formatDate, gettext} from 'utils';
import {getCoverageIcon} from '../utils';

import {Skeleton} from 'primereact/skeleton';

interface IProps {
    group: string;
    itemIds: Array<IAgendaItem['_id']>;
    itemsById: {[itemId: string]: IAgendaItem};
    itemsShown: boolean;
    toggleHideItems(group: string): void;
}

export function AgendaListGroupHeader({group, itemIds, itemsById, itemsShown, toggleHideItems}: IProps) {
    const coverageTypeCount: {[coverageType: string]: number} = {};
    let itemCount = 0;

    // Filter out Events/Planning that meet the following criteria
    // * Events with no planning items
    // * Events or Planning, no coverages at all
    // * Events or Planning, coverages fall on `group` date
    for (let itemIndex = 0; itemIndex < itemIds.length; ++itemIndex) {
        const item = itemsById[itemIds[itemIndex]];

        if (item.coverages == null || item.coverages.length === 0) {
            itemCount += 1;
            continue;
        }

        let coverageAdded = false;
        for (let coverageIndex = 0; coverageIndex < item.coverages.length; ++coverageIndex) {
            const coverage = item.coverages[coverageIndex];

            if (formatDate(moment(coverage.scheduled)) !== group) {
                continue;
            } else if (coverageTypeCount[coverage.coverage_type] == null) {
                coverageTypeCount[coverage.coverage_type] = 0;
                coverageAdded = true;
            }

            coverageTypeCount[coverage.coverage_type] += 1;
        }

        if (coverageAdded) {
            itemCount += 1;
        }
    }

    const coverageTypes = Object.keys(coverageTypeCount);

    return (
        <div className="list-group-header">
            <span className="badge rounded-pill badge--neutral">{itemIds.length}</span>
            {coverageTypes.length === 0 ? (
                <div className="list-group-header__title">
                    {gettext('More hidden')}
                </div>
            ) : (
                <React.Fragment>
                    <div className="list-group-header__title">
                        {gettext('More hidden')}
                    </div>
                    <div className="list-group-header__coverage-group">
                        {coverageTypes.map((coverageType) => (
                            <div key={coverageType} className="list-group-header__coverage-item">
                                <span className="wire-articles__item__icon" title="Some title">
                                    <i className={`icon--coverage-${getCoverageIcon(coverageType)}`} />
                                </span>
                                <span className="list-group-header__coverage-number">
                                    {coverageTypeCount[coverageType]}
                                </span>
                            </div>
                        ))}
                    </div>
                </React.Fragment>
            )}
            <div className="list-group-header__actions">
                <button
                    className="nh-button nh-button--tertiary nh-button--small"
                    onClick={() => {
                        toggleHideItems(group);
                    }}
                >
                    {itemsShown ? gettext('Hide') : gettext('Show all')}
                </button>
            </div>
        </div>
    );
}
