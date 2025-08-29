import * as React from 'react';
import {gettext} from 'utils';

import {ICompany, IEmbedPermissionUserAction, IEmbedContentType} from '../../interfaces';
import CheckboxInput from 'components/CheckboxInput';

interface IProps {
    company: ICompany;
    toggleCompanyEmbedPermission(contentType: IEmbedContentType, userAction: IEmbedPermissionUserAction): void;
}

interface IEmbedPermissionOptions {
    contentType: IEmbedContentType;
    label: string;
    separateDownloadPermission: boolean;
}

const embedPermissions: Array<IEmbedPermissionOptions> = [
    {
        contentType: 'featuremedia',
        label: gettext('FeatureMedia'),
        separateDownloadPermission: true,
    },
    {
        contentType: 'picture',
        label: gettext('Images'),
        separateDownloadPermission: false,
    },
    {
        contentType: 'video',
        label: gettext('Video'),
        separateDownloadPermission: true,
    },
    {
        contentType: 'audio',
        label: gettext('Audio'),
        separateDownloadPermission: true,
    },
    {
        contentType: 'embed_code',
        label: gettext('Embed Codes'),
        separateDownloadPermission: false,
    },
    {
        contentType: 'sd_product',
        label: gettext('Superdesk Products'),
        separateDownloadPermission: false,
    },
];

export function CompanyContentPermissions({company, toggleCompanyEmbedPermission}: IProps) {
    return (
        <div
            data-test-id="group--embedded-permissions"
            className="form-group"
            key="embedded-permissions"
        >
            <div className="list-item__preview-collapsible list-item__preview-collapsible--read-only list-item__preview-collapsible--small mb-2">
                <div className="list-item__preview-collapsible-header">
                    <i className="icon--arrow-right icon--rotate-90"></i>
                    <h3>{gettext('Embedded Content Permissions')}</h3>
                </div>
            </div>
            <div className="products-list__heading d-flex justify-content-between align-items-center">
                <span className="item--left">{gettext('Content Type')}</span>
                <span className="item--right">{gettext('Allow Download')}</span>
            </div>
            <ul className="list-unstyled">
                {embedPermissions.map(({contentType, label, separateDownloadPermission}) => (
                    <li key={`${contentType}_display`}>
                        <div className="products-list__product">
                            <div className="products-list__product-select">
                                <CheckboxInput
                                    name={`${contentType}_display`}
                                    label={label}
                                    value={(company.embed_permissions?.[contentType] ?? []).includes('display')}
                                    onChange={() => {
                                        toggleCompanyEmbedPermission(contentType, 'display');
                                    }}
                                />
                            </div>
                            {!separateDownloadPermission || !(company.embed_permissions?.[contentType] ?? []).includes('display') ? null : (
                                <div className="products-list__value">
                                    <CheckboxInput
                                        name={`${contentType}_download`}
                                        label=""
                                        value={(company.embed_permissions?.[contentType] ?? []).includes('download')}
                                        onChange={() => {
                                            toggleCompanyEmbedPermission(contentType, 'download');
                                        }}
                                    />
                                </div>
                            )}
                        </div>

                    </li>
                ))}
            </ul>
        </div>
    );
}
