import React from 'react';
import ReportsTable from './ReportsTable';

import {gettext} from 'utils';

interface IResult {
    _id: string;
    name: string;
    is_enabled: boolean;
    my_topics_count: number;
    company_topics_count: number;
}

interface IProps {
    results: Array<IResult>;
    print: boolean;
}


const SavedMyTopicsAndCompanyTopics = ({results, print}: IProps) => {
    const list = results && results.map((item: any) =>
        <tr key={item._id}>
            <td>{item.name}</td>
            <td>{item.is_enabled.toString()}</td>
            <td>{item.my_topics_count}</td>
            <td>{item.company_topics_count}</td>
        </tr>
    );

    const headers = [
        gettext('User'),
        gettext('Is Enabled'),
        gettext('My Topics'),
        gettext('Company Topics'),
    ];
    return results ? (<ReportsTable headers={headers} rows={list} print={print} />) : null;
};

export default SavedMyTopicsAndCompanyTopics;
