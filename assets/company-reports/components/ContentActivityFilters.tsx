import React, {useEffect, useMemo} from 'react';
import {Dispatch} from 'redux';
import {useDispatch, useSelector} from 'react-redux';
import {gettext} from 'utils';

import MultiSelectDropdown from 'components/MultiSelectDropdown';
import {REPORTS as REPORTS_API_ENDPOINTS} from 'company-reports/actions';
import {toggleFilter, fetchAggregations} from '../actions';
import CalendarButton from 'components/CalendarButton';
import moment from 'moment';


export const ContentActivityFilters = () => {
    const dispatch = useDispatch<Dispatch<any>>();
    const {
        sections,
        reportParams,
        apiEnabled,
        companies,
        reportAggregations
    } = useSelector((state: any) => state);

    const internalToggleFilter = (filterName: string, value: any) => {
        dispatch(toggleFilter(filterName, value));
    };

    const fetchReportAggregations = () => {
        dispatch(fetchAggregations(REPORTS_API_ENDPOINTS['content-activity']));
    };

    const onChangeSection = (field: string, value: string) => {
        internalToggleFilter('section', value);
        fetchReportAggregations();
    };

    const onDateChange = (value: any) => {
        internalToggleFilter('date_from', value);
        fetchReportAggregations();
    };

    const genreOptions = useMemo(() => {
        return (reportAggregations?.genres ?? [])
            .sort()
            .map((genre: string) => ({
                label: genre,
                value: genre,
            }));
    }, [reportAggregations?.genres]);

    const companyOptions = useMemo(() => {
        return companies
            .filter((company: any) => reportAggregations?.companies.includes(company._id))
            .map((company: any) => ({
                label: company.name,
                value: company.name,
            }));
    }, [companies, reportAggregations?.companies]);

    const filters = [
        {
            field: 'section',
            label: gettext('Section'),
            options: sections
                .filter((section: any) =>
                    ['wire', 'monitoring'].includes(section.group) ||
                    (section.group === 'api' && apiEnabled)
                )
                .map((section: any) => ({
                    label: section.name,
                    value: section.name,
                })),
            onChange: onChangeSection,
            showAllButton: false,
            multi: false,
            default: sections[0]?.name,
        },
        {
            field: 'genre',
            label: gettext('Genres'),
            options: genreOptions,
            onChange: internalToggleFilter,
            showAllButton: true,
            multi: true,
            default: [],
        },
        {
            field: 'company',
            label: gettext('Companies'),
            options: companyOptions,
            onChange: internalToggleFilter,
            showAllButton: true,
            multi: false,
            default: null,
        },
        {
            field: 'action',
            label: gettext('Actions'),
            options: [
                {label: gettext('Download'), value: 'download'},
                {label: gettext('Copy'), value: 'copy'},
                {label: gettext('Share'), value: 'share'},
                {label: gettext('Print'), value: 'print'},
                {label: gettext('Open'), value: 'open'},
                {label: gettext('Preview'), value: 'preview'},
                {label: gettext('Clipboard'), value: 'clipboard'},
                {label: gettext('API retrieval'), value: 'api'},
            ],
            onChange: internalToggleFilter,
            showAllButton: true,
            multi: true,
            default: [],
        }
    ];

    useEffect(fetchReportAggregations, []);

    return (
        <>
            <div>
                <CalendarButton
                    key='content_activity_date'
                    selectDate={onDateChange}
                    activeDate={reportParams?.date_from || moment()}
                />
            </div>

            {filters.map((filter: any) => {
                return (
                    <MultiSelectDropdown
                        key={filter.field}
                        {...filter}
                        values={reportParams[filter.field] || filter.default}
                    />
                );
            })}
        </>
    );
};
