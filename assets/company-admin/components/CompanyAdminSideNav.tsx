import * as React from 'react';

import {gettext} from 'assets/utils';

export function CompanyAdminSideNav() {
    return (
        <div className="side-navigation">
            <h3 className="a11y-only">{gettext('Settings Menu')}</h3>
            <ul>
                <li>
                    <a className="side-navigation__btn active">
                        {gettext('Company User Management')}
                    </a>
                </li>
            </ul>
        </div>
    );
}
