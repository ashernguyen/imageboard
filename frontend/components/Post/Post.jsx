import React from 'react';
import { Card } from 'antd';

const hElementStyle = {
    display : 'inline-block'
}

/**
 * @typedef {Object} File
 * @property {string} name
 * @property {string} url
 * 
 * @typedef {Object} Post
 * @property {number} id 
 * @property {string} title
 * @property {?string} author
 * @property {?string} contact
 * @property {?string} options
 * @property {string} message
 * @property {string} created_at
 * @property {string} updated_at
 * @property {Array<File>} files  
 */

/**
 * @param {Post} data
 * @returns {string} 
 */
const getAuthor = data => data.author || 'Аноним';

/**
 * @param {Object} param0
 * @property {Post} data 
 * @property {number} threadId
 * @property {boolean} sticked
 * @property {Array<number>} responses
 * @property {...any} props
 * 
 * @returns {React.ReactElement}
 */
const Post = ({ data, threadId, sticked, responses, ...props }) => (
    <Card {...props}>
        <div>
            <h3 style={hElementStyle}>{data.title}</h3>
            от
            <p style={hElementStyle}>
                {
                    data.contact ? (
                        <a href={data.contact}>
                            {getAuthor(data)}
                        </a>
                    ) : getAuthor(data)
                }
            </p>

            <a>
                #{data.id}
            </a>
        </div>

        <div>
            {!!data.options && `
                    Опции: 
                    ${data.options.split(',').join(', ')}
                `
            }

            {data.created_at}
        </div>

        <div key="files">
            {!!data.files && data.files.map((el, id) => (
                <Card key={id} style={hElementStyle}>
                    <img src={el.url} />
                    <p>{el.name}</p>
                </Card>
            ))}
        </div>

        <p>
            {data.message}
        </p>

        {!!responses && (
            <div key="responses">
                Ответы: 
                {responses.map((el, id) => (
                    <a key={id} href={`/threads/${threadId}#${el}`}>
                        {`>>${el}`}
                    </a>
                ))}
            </div>
        )}
    </Card>
)

export default Post;