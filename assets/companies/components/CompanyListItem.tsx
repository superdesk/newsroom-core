import React from 'react';
import classNames from 'classnames';
import {gettext, shortDate, isInPast} from 'utils';
import {getCountryLabel} from '../utils';
import {ICompany, ICountry} from 'interfaces';

interface IProps {
    company: ICompany;
    type?: {name: string};
    isActive: boolean;
    onClick: (id: string) => void;
    showSubscriberId: boolean;
    countries: Array<ICountry>;
}

export default function CompanyListItem({company, type, isActive, onClick, showSubscriberId, countries}: IProps) {
    return (
        <tr key={company._id}
            className={classNames({'table--selected': isActive, 'table-secondary': !company.is_enabled})}
            onClick={() => onClick(company._id)}
            tabIndex={0}
            data-test-id={`company-list-item--${company._id}`}
        >
            <td className="name">{company.name} {company.internal ? (
                <span className="badge badge--neutral-translucent me-2">{gettext('Internal')}</span>
            ) : null}</td>
            <td className="type">{type ? gettext(type.name) : ''}</td>
            {showSubscriberId && <td>{company.sd_subscriber_id}</td>}
            <td>{company.account_manager}</td>
            <td className={isInPast(company.expiry_date) ? 'text-danger' : undefined}>
                {(company.is_enabled ? gettext('Enabled') : gettext('Disabled'))}
            </td>
            <td>{company.contact_name}</td>
            <td>{company.phone}</td>
            <td>{getCountryLabel(company.country, countries)}</td>
            <td>{shortDate(company._created)}</td>
            <td>{company.expiry_date && shortDate(company.expiry_date.substring(0, 10), false)}</td>
        </tr>
    );
}